---
schema_version: '1'
id: stack.rockchip-rknn.detection
kind: stack_guide
applies_to:
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-kernel-config
- source.cached-vendor-dts
- source.rknn-project
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Rockchip RKNPU and compatible RKNN runtime: detection

Inspect platform driver, actual access nodes, runtime library, and package versions. Do not fix the device name to /dev/rknpu; discover the actual driver/runtime path.

Map DRM nodes to drivers via the `DRIVER=` field in `/sys/class/drm/*/device/uevent`. Mind the `device/` level: `card*/uevent` itself holds only major/minor numbers and no `DRIVER`, so a path missing `device/` returns nothing. RKNPU may be bound to a card or a renderD node; check this field instead of guessing by number order, and never treat enumeration order as application choice.

Package and ldconfig listings cover only their own inventories. If RKNN is absent there, report it as not found in those sources; inspect the application's configured library path, loaded libraries and binding/environment before declaring its runtime missing. Driver binding or debug counters do not establish userspace readiness, and an idle counter does not prove the device has never been used. Preserve the unknown application layer rather than prescribing installation from incomplete discovery.
