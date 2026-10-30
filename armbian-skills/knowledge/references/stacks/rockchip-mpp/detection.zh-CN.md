---
schema_version: '1'
id: stack.rockchip-mpp.detection
kind: stack_guide
applies_to:
  capabilities:
  - vpu
  stack_ids:
  - rockchip-mpp
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
- source.ffmpeg
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Rockchip MPP kernel service + compatible media userspace: detection

检查实际 MPP 驱动/节点、用户态库、FFmpeg/GStreamer 构建；ffmpeg -hwaccels 仅是构建功能列表。枚举命令不等于已解码。
