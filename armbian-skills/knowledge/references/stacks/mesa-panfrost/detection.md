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

# Panfrost kernel and Mesa userspace: detection

Read DRM binding, /dev/dri, Mesa dependencies, and runtime environment. Check EGL/GLES/OpenCL/Vulkan separately. A capability query does not automatically start rendering or change the desktop.
