---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.quirks
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.v1.0.interfaces
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.cached-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](quirks.md) | [简体中文](quirks.zh-CN.md)

# Board constraints and known differences

- Distinguish full-system DevKit from Module Dev Kit; carriers/connectors/pinouts are not interchangeable.
- Cached vendor Linux compatible contains spaces; mainline/U-Boot uses hyphens. Preserve exact strings and sources rather than normalizing away differences.
-26 local PIN labels disagree with schematic J3 pads. See [documented mapping](schematic-mapping.md); retain incorrect source labels for traceability, not output control.
- Source associates user-led with GPIO-expander offset 9. Confirm the actual driver and prefer the LED subsystem without seizing the line.
- USB/PCIe power/reset, Wi-Fi/BT, fan, and EEPROM WP are system resources, not default direct application controls.
- Camera checks require actual sensor, IQ/3A, color, exposure/white balance, and output; capture or service running alone is insufficient.
