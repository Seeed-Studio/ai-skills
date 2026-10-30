---
schema_version: '1'
id: stack.mesa-panfrost.detection
kind: stack_guide
applies_to:
  capabilities:
  - gpu
  stack_ids:
  - mesa-panfrost
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-kernel-config
- source.mesa-panfrost
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Panfrost kernel + Mesa userspace: detection

只读检查 DRM 绑定、/dev/dri、Mesa 依赖与运行环境；EGL/GLES/OpenCL/Vulkan 需分别检测。能力查询不自动启动渲染或改桌面。
