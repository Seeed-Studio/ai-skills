---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.overview
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
required_refs:
- board.seeed.recomputer-rk3576-devkit
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout
sources:
- source.seeed-product
- source.local-board-config
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# RK3576-20/30 application entry point

This profile describes the reComputer RK3576-20/30 full-system DevKit reference design, corresponding to Armbian recomputer-rk3576-devkit. Module Dev Kit uses another carrier and cannot share this pinout. Confirm actual product, PCB revision, and orientation for each device.

- [Board data](board.yaml): product interfaces, exact compatible candidates, EEPROM routing codes, and DTB differences.
- [Official 40-pin labels](revisions/v1.0/official-pinout.md): all 40 positions, diagram orientation, and power/GND declarations.
- [Schematic-to-SoC mapping](revisions/v1.0/schematic-mapping.md): nets, pads, local offsets, translation paths, and 26 incorrect Linux-label differences.
- [Interface sources/conflicts](revisions/v1.0/interfaces.md): vendor labels are not an authoritative physical pinout.
- [Overlay source inventory](overlay-inventory.yaml) and [image configuration](revisions/v1.0/configuration.md): candidate functions/conflicts; target installation/enablement requires separate checks.
- [Peripherals](../../../platforms/rockchip/rk3576/peripherals.md) and [accelerators](../../../platforms/rockchip/rk3576/accelerators.md): GPIO/I2C/UART/SPI/CAN/PWM, NPU/GPU/VPU prerequisites.
- [Information to confirm](questions.md).

Analyze existing language, build, and business entry points before choosing the actual stack. A node, one successful feature, or a documented label cannot replace application-level verification.
