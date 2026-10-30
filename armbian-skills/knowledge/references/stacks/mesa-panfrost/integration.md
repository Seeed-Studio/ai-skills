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

# Panfrost kernel and Mesa userspace: integration

The referenced board configuration selects panfrost and skips proprietary libmali. Integrate using the actual API/context without overwriting system EGL libraries. Language-native modules must match the ABI.
