---
schema_version: '1'
kind: stack_guide
applies_to:
  capabilities:
  - gpu
  soc_ids:
  - rockchip.rk3588
  stack_ids:
  - mesa-panthor
required_refs:
- stack.mesa-panthor
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-rk3588-board
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
id: stack.mesa-panthor.detection
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Panthor / Mesa detection

本地板级源码选择 Panthor/Mesa，但不证明目标已启用。检查当前 GPU 绑定为 panthor 而非闭源 Mali，并核对固件、Mesa/loader、DRM 设备身份和真实 API；不套用 Panfrost 的 kernel driver 版本或固定 render 节点。
