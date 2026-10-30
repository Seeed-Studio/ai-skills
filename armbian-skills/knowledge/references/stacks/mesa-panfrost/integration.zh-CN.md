---
schema_version: '1'
id: stack.mesa-panfrost.integration
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

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Panfrost kernel + Mesa userspace: integration

本地 board 配置选择 panfrost 并跳过闭源 libmali。应用按实际 API 和上下文实现，不覆盖系统 EGL 库；语言 native 模块需匹配 ABI。
