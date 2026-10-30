---
schema_version: '1'
id: board.seeed.recomputer-rk3588-devkit.overview
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3588-devkit
required_refs:
- board.seeed.recomputer-rk3588-devkit
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-rk3588-board
- source.local-rk3588-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# recomputer-rk3588-devkit reference entry point

Vendor compatible is `seeed studio,recomputer rk3588 devkit`; mainline uses `seeed,recomputer-rk3588-devkit`. Match each exactly; neither proves PCB revision. Discover the actual GPU driver. The NPU may expose DRM nodes, so do not hardcode renderD numbers or conclude it is absent because /dev/rknpu is missing.

Read [board data](board.yaml) and [platform data](../../../platforms/rockchip/rk3588/platform.yaml). Add current compatible/kernel/driver facts before selecting the actual stack. Unknown revision does not prevent investigation or offline work independent of header pins.

See the [full 40 J10 interface guide](revisions/v1.0/interfaces.md) for routing, voltage paths, mux candidates and the shared net on pins23/40. Documentary coverage does not establish current hardware readiness.
