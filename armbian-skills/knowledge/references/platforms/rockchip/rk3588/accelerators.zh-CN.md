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

# rk3588 加速接入范围

本地板级构建配置选择 Panthor/Mesa；使用独立的 stack.mesa-panthor 资料，不套用 Panfrost 内核 driver。检查目标实际 panthor/Mali 绑定、固件与 Mesa/API，不能使用 RK3576 的驱动版本或 render 节点。RKNN/MPP 也需各自核对 RK3588 用户态与输入。
