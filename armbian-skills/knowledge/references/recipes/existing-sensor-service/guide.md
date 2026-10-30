---
schema_version: '1'
id: recipe.existing-sensor-service.guide
kind: recipe_guide
applies_to:
  capabilities:
  - i2c
  operations:
  - sensor.read
required_refs:
- recipe.existing-sensor-service
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# Extending an existing collection service

Inspect existing business/collection entry points and preserve language/build conventions. Confirm sensor protocol and external bus. Add readings, timestamps, stale/error state, and integration into the original API. A single collection task owns persistent resources. Check real responses, disconnect/recovery, timeout, and business regression, deploying as the actual service user. Without a specified device, real project, and hardware, no register/address defaults are directly executable.
