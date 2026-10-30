---
schema_version: '1'
id: stack.mesa-panfrost.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Panfrost kernel and Mesa userspace: verification

Use a small example matching the actual API, recording renderer/device and output. Identify llvmpipe/software fallback and verify compute separately. Static references do not establish the current renderer or availability of every API.
