---
schema_version: '1'
id: platform.rockchip.rk3588.accelerators
kind: platform_guide
applies_to:
  soc_ids:
  - rockchip.rk3588
required_refs:
- platform.rockchip.rk3588
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
updated_at: '2026-10-19'
---

[English](accelerators.md) | [简体中文](accelerators.zh-CN.md)

# RK3588 accelerator integration scope

Board build configuration selects Panthor/Mesa. Read the separate stack.mesa-panthor references rather than applying the Panfrost kernel driver. Check actual panthor/Mali binding, firmware, Mesa/APIs, and current nodes; do not inherit RK3576 driver versions or render paths. RKNN/MPP each require RK3588 userspace and input checks.
