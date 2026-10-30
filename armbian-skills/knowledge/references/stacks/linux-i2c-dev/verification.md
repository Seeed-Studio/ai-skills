---
schema_version: '1'
id: stack.linux-i2c-dev.verification
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
updated_at: '2026-10-20'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Linux i2c-dev: verification

Require a specified external device and confirmed wiring. Check protocol responses, data conversion, disconnection, and original business regression. Bus numbers do not establish external/internal routing or exclusivity. Trace header, controller, translators/pullups, shared devices, and current owners first. Do not scan shared buses or force access to driver-owned addresses.
