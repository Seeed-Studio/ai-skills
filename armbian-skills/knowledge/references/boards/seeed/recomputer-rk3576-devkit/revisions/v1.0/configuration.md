---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.configuration
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.overlays
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-bootscript
- source.local-overlays-note
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](configuration.md) | [简体中文](configuration.zh-CN.md)

# Image configuration and enablement checks

Host board configuration declares vendor/edge. Vendor uses rockchip/rk3576-recomputer-rk3576-devkit.dtb; the non-vendor branch uses rockchip/rk3576-recomputer-devkit.dtb. Confirm the current branch from kernel, boot configuration, and source evidence. Boot scripts may use EEPROM routing or .dist fallback, so configured fdtfile does not prove the file actually loaded.

The EEPROM routing prefix uses six-byte magic rk35xx followed by 00A0 for this board or 01A0 for Module Dev Kit. Ten bytes suffice for this format check. The routing code is not PCB V1.0, and full EEPROM contents must not become generic probe output. If actual contents do not match, retain unknown identity rather than rewriting EEPROM to fit a script.

Overlay-inventory.yaml records host source candidates. Before enabling one, inspect target DTBO presence, current overlays, boot path, resource conflicts, and precise pinctrl. Do not change overlays/reboot merely to populate documentation.

The uart5 overlay disables spi3. CAN0/1, UART3, and PWM2 use different pinctrl groups, so physical labels cannot be applied mechanically. Preserve original boot configuration for recovery and use the image's actual boot method. Secure Boot FIT and ordinary file boot cannot share an unverified configuration procedure.

DTBO presence is not enablement; check current running DT and boot paths separately.
