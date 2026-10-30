---
schema_version: '1'
id: stack.linux-i2c-dev.detection
kind: stack_guide
applies_to:
  capabilities:
  - i2c
  stack_ids:
  - linux-i2c-dev
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-kernel-config
- source.cached-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Linux i2c-dev: detection

`i2cdetect -l` lists adapters only. Inspect `/sys/class/i2c-dev` and bound drivers. Do not perform an unrestricted i2cdetect scan. Resolve bus numbering on the current target.
