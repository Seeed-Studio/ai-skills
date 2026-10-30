---
schema_version: '1'
id: platform.rockchip.rk3576.accelerators
kind: platform_guide
applies_to:
  soc_ids:
  - rockchip.rk3576
required_refs:
- stack.rockchip-rknn
- stack.mesa-panfrost
- stack.rockchip-mpp
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-kernel-config
- source.cached-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](accelerators.md) | [简体中文](accelerators.zh-CN.md)

# RK3576 accelerator stack candidates

| Capability | Candidate stack | Integration/evidence |
|---|---|---|
| NPU | stack.rockchip-rknn | RK3576 model, driver/runtime, language binding, correct fixed-input output, and NPU execution evidence |
| GPU graphics | stack.mesa-panfrost | Actual renderer, EGL/GLES or other API, desktop/headless context, and access |
| GPU compute | Detect actual APIs separately | Graphics success does not establish OpenCL/Vulkan or a particular compute framework |
| VPU decode/encode | stack.rockchip-mpp | Actual MPP/media framework, codec/profile/bit depth/resolution, and output |

Nominal TOPS, configuration, or feature lists do not establish working support. Check real service/container access rather than relying on a root-shell example.
