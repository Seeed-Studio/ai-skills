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
id: stack.mesa-panthor.verification
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Panthor / Mesa verification

Record actual renderer/device/provider and output, identifying software rendering. Verify graphics and compute separately. Build configuration alone cannot establish RK3588 hardware or application success.
