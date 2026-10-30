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
id: stack.mesa-panthor.detection
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Panthor / Mesa detection

Board source selects Panthor/Mesa but does not prove target enablement. Inspect actual panthor versus proprietary Mali binding, firmware, Mesa/loader, DRM identity, and APIs. Do not reuse Panfrost kernel-driver versions or fixed render-node numbers.
