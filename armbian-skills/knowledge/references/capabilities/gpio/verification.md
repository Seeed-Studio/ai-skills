---
schema_version: '1'
id: capability.gpio.verification
kind: capability_guide
applies_to:
  capabilities:
  - gpio
required_refs:
- capability.gpio
- common.verification
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# GPIO verification

Check the ordering of initial level/direction configuration, normal holding, expiry, cancellation, failure/crash, and repeated startup. Releasing a line request does not guarantee its level; `kill -9` cannot execute userspace cleanup. Record logical active/inactive separately from physical high/low. Use external hardware when a safe state is required. Handle contention through the actual request without forcibly taking ownership.
