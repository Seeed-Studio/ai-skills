---
schema_version: '1'
id: stack.linux-gpio-chardev.verification
kind: stack_guide
applies_to:
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs: []
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.cached-vendor-dts
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# GPIO stack verification

Using confirmed connector mapping, electrical conditions, wiring, and ownership, check initial value, holding, expiry, busy/races, cancellation, errors, and release. Readback establishes an API observation, not physical voltage. Test the actual user/container; root success does not establish ordinary-user access.

Follow [recovery](recovery.md) to check request release, direction/configuration, instrument voltage, and the external device separately. Restore a setting only when its original state is known and appropriate. Do not universally force LOW or input. Record unmeasured, failed, and unknown outcomes.
