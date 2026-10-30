---
schema_version: '1'
id: stack.linux-i2c-dev.integration
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

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Linux i2c-dev: integration

Prefer an existing driver's business interface. For raw I2C, choose access according to the datasheet, runtime permissions, and project-language binding. Handle repeated starts, read/write direction, data units, timeouts, and bounded retries.
