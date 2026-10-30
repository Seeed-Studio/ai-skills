#!/usr/bin/env python3
"""Read-only, bounded Armbian capability collection; no credentials or writes.

Run on the target, including via: ssh TARGET 'python3 -' < probe_device.py
This is an inventory probe, not a functional hardware validation.
"""
import datetime
import argparse
import glob
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

LIMIT = 32768


def read(path, binary=False, limit=LIMIT):
    try:
        with open(path, "rb") as stream:
            raw = stream.read(limit + 1)
        truncated = len(raw) > limit
        raw = raw[:limit]
        return {"status": "ok", "value": list(raw) if binary else raw.decode("utf-8", "replace").rstrip("\x00\n"), "truncated": truncated}
    except OSError as exc:
        return {"status": "unknown", "error": type(exc).__name__}


def release(path, fields):
    result = read(path)
    if result["status"] == "ok":
        result["value"] = {key: value.strip().strip('"\'') for line in result["value"].splitlines()
                           if "=" in line for key, value in [line.split("=", 1)] if key in fields}
    return result


def command(args, timeout=8, include_lines=None):
    exe = shutil.which(args[0])
    if exe is None:
        return {"status": "unknown", "reason": "tool_missing"}
    # Stream into an anonymous pipe and enforce byte/time limits while reading.
    import selectors
    import signal
    import time
    try:
        proc = subprocess.Popen([exe, *args[1:]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                env={**os.environ, "LC_ALL": "C"}, start_new_session=True)
    except OSError as exc:
        return {"status": "unknown", "reason": "execution_error", "error": type(exc).__name__}
    output = bytearray()
    pending = bytearray()
    raw_bytes = 0
    terms = tuple(term.lower().encode('ascii') for term in (include_lines or []))
    def collect(line):
        if any(term in line.lower() for term in terms):
            output.extend(line)
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout
    reason = None
    try:
        while selector.get_map():
            left = deadline - time.monotonic()
            if left <= 0:
                reason = "timeout"
                break
            for key, _ in selector.select(min(left, 0.25)):
                chunk = os.read(key.fileobj.fileno(), min(4096, LIMIT + 1 - len(output)))
                if not chunk:
                    if terms and pending:
                        collect(bytes(pending))
                        pending.clear()
                    selector.unregister(key.fileobj)
                else:
                    raw_bytes += len(chunk)
                    if terms:
                        if raw_bytes > LIMIT * 64:
                            reason = "raw_output_limit"
                            break
                        pending.extend(chunk)
                        while b'\n' in pending:
                            line, _, rest = pending.partition(b'\n')
                            pending[:] = rest
                            collect(bytes(line) + b'\n')
                        if len(pending) > LIMIT:
                            reason = "line_length_limit"
                            break
                    else:
                        output.extend(chunk)
                if len(output) > LIMIT:
                    reason = "output_limit"
                    break
            if reason:
                break
        if not reason:
            try:
                code = proc.wait(timeout=max(0.01, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                reason = "timeout"
        if reason:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            code = proc.wait(timeout=2)
        return {"status": "ok" if code == 0 and not reason else "unknown", "exit_code": code,
                "reason": reason, "output": bytes(output[:LIMIT]).decode("utf-8", "replace"),
                "raw_output_bytes": raw_bytes, "selected_line_patterns": list(include_lines or [])}
    finally:
        selector.close()
        proc.stdout.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eeprom-identity', action='store_true',
                        help='Opt-in rk35xx magic/board-code read; use only on a confirmed matching board')
    options = parser.parse_args(argv)
    model = read("/proc/device-tree/model")
    compatible = read("/proc/device-tree/compatible", binary=True)
    if compatible["status"] == "ok":
        compatible["value"] = bytes(compatible["value"]).decode("utf-8", "replace").strip("\x00").split("\x00")
    result = {
        "schema_version": "1", "probe": "armbian-capabilities-readonly-v1",
        "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "inventory_only": True,
        "execution_context": {"effective_uid": os.geteuid(), "application_access_tested": False},
        "identity": {"model": model, "compatible": compatible, "architecture": platform.machine(), "kernel_release": platform.release()},
        "os": release("/etc/os-release", {"ID", "VERSION_ID", "PRETTY_NAME"}),
        "armbian": release("/etc/armbian-release", {"BOARD", "BOARD_NAME", "BOARDFAMILY", "BRANCH", "VERSION", "LINUXFAMILY"}),
        "boot_config": release("/boot/armbianEnv.txt", {"fdtfile", "overlay_prefix", "overlays", "user_overlays"}),
        "nodes": {pattern: sorted(glob.glob(pattern)) for pattern in ["/dev/gpiochip*", "/dev/i2c-*", "/dev/spidev*", "/dev/ttyS*", "/dev/ttyFIQ*", "/dev/dri/*", "/dev/video*", "/dev/media*", "/dev/mpp*", "/dev/rknpu*", "/dev/rga*", "/sys/class/net/can*", "/sys/class/pwm/pwmchip*"]},
        "tools": {}, "sysfs": {}, "eeprom_identity_prefix": {},
        "not_performed": ["gpio_line_request", "gpio_write", "i2c_bus_scan", "sensor_register_access", "service_change", "overlay_change", "inference", "rendering", "video_streaming", "reboot"],
    }
    commands = {
        "gpiodetect": ["gpiodetect"], "gpioinfo": ["gpioinfo"], "gpiod_version": ["gpioinfo", "--version"],
        "i2c_bus_list": ["i2cdetect", "-l"], "pci": ["lspci", "-nnk"], "usb_tree": ["lsusb", "-t"],
        "video_devices": ["v4l2-ctl", "--list-devices"], "ffmpeg_version": ["ffmpeg", "-version"],
        "ffmpeg_hwaccels": ["ffmpeg", "-hide_banner", "-hwaccels"],
        "packages": ["dpkg-query", "-W", "-f=${db:Status-Status}\t${Package}\t${Version}\n"],
        "runtime_libraries": ["ldconfig", "-p"],
    }
    filters = {
        "packages": ["gpiod", "rknn", "mpp", "mesa", "mali", "rkaiq", "ffmpeg"],
        "runtime_libraries": ["rknn", "rockchip_mpp", "libmpp", "libegl", "libgles", "libvulkan", "libmali", "libgpiod"],
    }
    for name, args in commands.items():
        result["tools"][name] = command(args, include_lines=filters.get(name))
    # Metadata/state reads only. Do not dump EEPROM serials, network addresses,
    # arbitrary environment variables, application files or shell histories.
    patterns = ["/sys/class/thermal/thermal_zone*/type", "/sys/class/thermal/thermal_zone*/temp",
                "/sys/class/hwmon/hwmon*/name", "/sys/class/hwmon/hwmon*/fan1_input",
                "/sys/class/leds/*/trigger", "/sys/class/leds/*/brightness",
                "/sys/class/gpio/gpiochip*/label", "/sys/class/gpio/gpiochip*/ngpio",
                "/sys/bus/gpio/devices/gpiochip*/label", "/sys/bus/gpio/devices/gpiochip*/ngpio",
                "/sys/kernel/debug/gpio", "/sys/kernel/debug/pinctrl/*/pinmux-pins"]
    for pattern in patterns:
        for path in sorted(glob.glob(pattern))[:32]:
            result["sysfs"][path] = read(path)
    eeprom_paths = sorted(glob.glob("/sys/bus/i2c/devices/*-0057/eeprom"))[:4] if options.eeprom_identity else []
    if not options.eeprom_identity:
        result['not_performed'].append('eeprom_identity_read')
    for path in eeprom_paths:
        identity = read(path, binary=True, limit=10)
        if identity["status"] == "ok":
            prefix = bytes(identity.pop("value"))
            if prefix.startswith(b"rk35xx") and len(prefix) == 10:
                identity["value"] = {"magic": "rk35xx", "board_code": prefix[6:10].decode("ascii", "replace")}
            else:
                identity["value"] = None
                identity["format_hint"] = "legacy_serial_prefix" if prefix.startswith(b"SN:") else "unrecognized"
                identity["reason"] = "not_supported_board_identity_format"
        result["eeprom_identity_prefix"][path] = identity
    result["bound_drivers"] = {path: os.path.basename(os.path.realpath(path)) for path in sorted(glob.glob("/sys/bus/platform/devices/*/driver"))}
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
