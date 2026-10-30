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

# Rockchip MPP kernel service and media userspace: verification

Use a specified short video to verify decoder and encoder separately, actual hardware initialization, and output frame count/duration/quality. Establish codec, resolution, API, and processing speed on the target rather than inferring them from static references.
