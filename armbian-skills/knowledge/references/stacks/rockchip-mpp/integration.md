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

# Rockchip MPP kernel service and media userspace: integration

Choose a media library or bounded process pipeline to fit the existing application. Check pixel formats, timestamps, buffers, and cancellation. Vendor FFmpeg interfaces cannot be assumed compatible with other versions.
