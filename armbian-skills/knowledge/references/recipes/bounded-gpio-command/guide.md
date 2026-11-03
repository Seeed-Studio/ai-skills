---
schema_version: '1'
id: recipe.bounded-gpio-command.guide
kind: recipe_guide
applies_to:
  capabilities:
  - gpio
  operations:
  - gpio.output
required_refs:
- recipe.bounded-gpio-command
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.libgpiod-tools
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-11-03'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# A bounded GPIO feature for beginners

Explain the connector, logic levels, external load, and current-limiting/measurement preparation. Confirm reliable pin-to-net mapping, electrical conditions, mux, and current ownership before choosing the project's command/program. Hold the request until expiry/cancellation and record exit/release behavior. Check physical effect and busy/cancel/failure paths. Do not create a daemon/service by default. Without a reliable mapping, complete code/logic tests first without driving output.

## Deliver a conditional finite CLI check

Resolve the board/revision, connector, physical pin → pad → controller → **current** chip path/local offset. Read the selected electrical path and [wiring guidance](../../common/wiring-diagrams.md), then inspect [current metadata and tool version/help](../../stacks/linux-gpio-chardev/detection.md). Free consumer metadata does not settle mux, external wiring or request races. A wrong-controller or brief released request is not evidence of damaged GPIO.

If drive current/load compatibility is unknown, do not reconnect an LED to try again. Provide a conditional high-impedance voltmeter check first, with the LED disconnected. Show the signal/red and GND/black endpoints and the board's orientation when supported. Do not run commands on the development host.

For a target whose `gpioset --help` confirms **2.x `-c`, `--hold-period` and `--toggle` ending in 0**, the following is a procedure to deliver after mapping/electrical/mux/owner checks, not a discovery command. Set the variables to the verified current mapping; they have no default chip or line:

```sh
: "${chip:?Set the verified /dev/gpiochipN path}"
: "${offset:?Set the verified chip-local numeric offset}"
# 10s is an adjustable read-the-meter example, not an acceptance threshold.
gpioset -c "$chip" --hold-period 10s --toggle 0 "${offset}=1"
```

Here `--hold-period` sets a minimum hold; **it is not a stop timer on its own**. The terminal `--toggle 0` makes this check exit after that hold without cycling to another requested value. Keep it in the foreground; Ctrl+C cancels early. Record voltage while the request is held. If the meter reading is not obtained before release, mark it unmeasured; do not use the later voltage as the held result. If a low-level reading is required, recheck ownership and run the same finite command with `${offset}=0`; do not assume release is the low-level test. Do not use `gpioget` to read a held output.

After normal exit or cancellation, use the target-version-supported `gpioinfo` and mux metadata to confirm this consumer is gone. Busy/permission/unsupported-option/bias errors stop that stage; no forced ownership or silent fallback. Follow [recovery](../../stacks/linux-gpio-chardev/recovery.md): report release, direction/configuration and measured voltage separately, restore only known appropriate settings, and keep unknown bias/post-restoration voltage explicit. A finite command still needs the circuit's failure/power-loss behavior considered; it is not a safety interlock.

If those target options differ or are unavailable, deliver a finite lifecycle with the project's verified native API or supervisor instead; do not install a new daemon merely for a GPIO check.

Syntax reference: [official gpioset documentation](https://libgpiod.readthedocs.io/en/master/gpioset.html); upstream development documentation is not evidence of the installed target version.
