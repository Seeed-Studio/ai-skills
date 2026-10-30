---
schema_version: '1'
id: stack.rockchip-mpp.integration
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

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Rockchip MPP kernel service + compatible media userspace: integration

根据现有应用选择媒体库或有限进程流水线，校验像素格式、时间戳、缓冲和取消；厂商 FFmpeg 接口不能自动套用于其他版本。
