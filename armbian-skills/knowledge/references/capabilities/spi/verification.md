---
schema_version: '1'
id: capability.spi.verification
kind: capability_guide
applies_to:
  capabilities:
  - spi
required_refs:
- capability.spi
- common.verification
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# SPI verification

Gather evidence layer by layer: node enumeration → pin muxing → connector routing and electrical conditions → application access → device communication. Each layer's evidence supports only that layer's conclusion.

An existing spidev node proves only that the controller enumerated. Pin muxing can be checked on the target via `/sys/kernel/debug/pinctrl/*/pinmux-pins` (e.g. `function spi1 group spi1m0-cs0`): that record proves the pads are claimed by the controller, not that header routing, the peer beyond the level translator, or application access work. Do not conclude "no overlay needed / routed to the connector" from "no SPI entry in the overlay list + node present" — a base DTB can enable the node; overlays are only one configuration source.

## Backlight and direct GPIO drive

While the module circuit is unknown, the BL drive topology (logic enable input, LED power rail, transistor/op-amp driver) is unknown: assert none of them, and give no direct-drive feasibility, series resistor value, or power-on order guarantees on that basis. Tying BLK to a fixed level (3V3 included) is likewise powering an unknown circuit: enable polarity and the presence of onboard current limiting are both unconfirmed, so it must not be written as a default first-check step, and no "it will light / stay lit once connected" promise may be made. When such a check is needed, list the prerequisites case by case (active-high/low enable, onboard limiter present or not) and bound it with a series-resistor voltage drop or current measurement. The check source is the module schematic/datasheet; if unavailable, deliver the possibilities plus a discriminating measurement and stay conditional. gpioget readback itself requests the line and may change its direction/level; it is not an undisturbed measurement or proof of physical voltage.

## Limits of loopback verification

A MOSI↔MISO jumper loopback proves only the controller-to-header data path (including the level translator). Equal readback does not prove CS routing — the loopback does not depend on a CS peer — nor external device protocol, initialization, or display function. CS physical routing needs an instrument (scope/logic analyzer) or a real device's protocol response. A loopback answers only "data path open/not open" and is not acceptance of a display or other peripheral.

## spi_ioc_transfer layout

Never hand-write the `struct spi_ioc_transfer` layout from memory. Fields differ across kernel versions (newer kernels add `word_delay_usecs` with a single-byte `pad`; older ones end with a 2-byte `pad`). Read the target's `/usr/include/linux/spi/spidev.h` first and assert that `struct.calcsize` matches the `SPI_IOC_MESSAGE(1)` size bits (currently 32 bytes, `0x40206b00`). Minimal loopback (jumper MOSI↔MISO and obtain wiring authorization first; without the jumper a FAIL is the expected result, not a fault):

```bash
python3 - <<'EOF'
import ctypes, fcntl, os, struct
DEV = '/dev/spidev1.0'  # replace with the actual target node
FMT = '=QQIIHBBBBBB'    # verify against the target spidev.h: u64 u64 u32 u32 u16 6*u8
assert struct.calcsize(FMT) == 32 == ((0x40206B00 >> 16) & 0x3FFF)
fd = os.open(DEV, os.O_RDWR)
fcntl.ioctl(fd, 0x40016B01, struct.pack('=B', 0))        # SPI_IOC_WR_MODE
fcntl.ioctl(fd, 0x40016B03, struct.pack('=B', 8))        # SPI_IOC_WR_BITS_PER_WORD
fcntl.ioctl(fd, 0x40046B04, struct.pack('=I', 1000000))  # SPI_IOC_WR_MAX_SPEED_HZ
tx = bytes(range(16)); n = len(tx)
bi = ctypes.create_string_buffer(tx); bo = ctypes.create_string_buffer(n)
xf = struct.pack(FMT, ctypes.addressof(bi), ctypes.addressof(bo), n,
                 1000000, 0, 8, 0, 0, 0, 0, 0)
fcntl.ioctl(fd, 0x40206B00, xf)                          # SPI_IOC_MESSAGE(1)
print('loopback:', 'OK' if bo.raw[:n] == tx else 'FAIL ' + bo.raw[:n].hex())
EOF
```

Bus/CS numbers and speed/mode limits follow the target's nodes and the module specification. A running script proves only a correct ABI, not a connected peer; when delivering loopback steps, also state the expected result, the meaning of failure, and the required wiring.
