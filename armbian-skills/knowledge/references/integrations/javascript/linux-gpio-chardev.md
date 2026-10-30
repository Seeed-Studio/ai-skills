---
schema_version: '1'
id: integration.javascript.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - javascript
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.javascript.guide
- stack.linux-gpio-chardev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# JavaScript / linux-gpio-chardev

Determine whether the project uses the kernel GPIO UAPI or libgpiod, checking their ABIs and binding versions separately. One owner must hold the request until expiry/cancellation. Configure direction and initial value together; report busy as a business error rather than forcibly taking ownership.

Check the chosen library and pinned version in the actual project. This guide defines integration and acceptance constraints, not certification of a language binding. Configure the currently resolved device identity and resource/address; do not hardcode another board's nodes into generic source.
