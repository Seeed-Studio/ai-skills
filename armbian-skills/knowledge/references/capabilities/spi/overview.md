---
schema_version: '1'
id: capability.spi
kind: capability
applies_to:
  capabilities:
  - spi
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-spidev
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-30'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# SPI application integration

Confirm the external device, voltage, chip select, mode, bit order, and speed. Resolve nodes from actual device identity. Read/write and combined transactions have different chip-select behavior; choose the interface required by the device protocol. Use an existing driver's interface rather than forcibly rebinding it. A successful SPI call can occur without a device response: check peer protocol/data or an explicit loopback.

A spidev node establishes enumeration, not the external connector route, current mux, application access or display initialization. Resolve those conditions before deciding whether a device-tree change is needed. For a short migration question with unknown PCB/module, first obtain that identity rather than supplying an assumed complete wiring table.

Display DC/RST/BL may need separate GPIO. Follow [GPIO detection](../../stacks/linux-gpio-chardev/detection.md) for current tool/API version, mapping and ownership before giving an output command. BL can be a logic enable or LED power input: check the module circuit, current and translator/load limits. Equal nominal voltage or a typical module's onboard limiter does not establish direct GPIO drive compatibility. While the module circuit is unknown, tying BL/RST to a fixed level (3V3 included) is also powering an unknown circuit: do not write it as a default first-check step and never promise "it will light / stay lit once connected"; list enable-polarity and current-limiting prerequisites case by case, or bound it with measurements per [SPI verification](verification.md). Keep unknown BL supply/enable requirements unresolved in the wiring table itself; a later caveat does not make an executable direct-drive instruction conditional. Before supplying a gpioset command, check the target version/help, line ownership and electrical prerequisites: 2.x selects the chip with `-c`, while 1.x uses positional-chip syntax. Select SPI mode/rate from the actual module requirements, not trial-and-error defaults.
