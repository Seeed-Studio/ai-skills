---
schema_version: '1'
id: stack.rockchip-mpp.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Rockchip MPP kernel service + compatible media userspace: verification

指定短视频分别验证 decoder/encoder、实际硬件初始化及输出帧/时长/质量；当前 codec、resolution、API和处理速度均未知。
