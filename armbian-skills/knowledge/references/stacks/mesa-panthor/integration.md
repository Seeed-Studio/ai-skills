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
id: stack.mesa-panthor.integration
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Panthor / Mesa integration

Keep the project's graphics/compute framework. Choose integration for actual EGL/GLES/Vulkan APIs, headless/desktop context, and user/container environment. Panthor binding does not guarantee every Mesa API or compute framework. Establish compatibility, impact, and recovery before installing/switching graphics stacks.
