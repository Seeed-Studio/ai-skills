---
schema_version: '1'
id: capability.i2c
kind: capability
applies_to:
  capabilities:
  - i2c
required_refs:
- common.capability-evidence
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

[English](overview.md) | [简体中文](overview.zh-CN.md)

# I2C application development

Confirm the external bus, device model, supply, signal levels, and address. Prefer a kernel driver or IIO/hwmon interface; use i2c-dev when needed. Do not scan every bus by default, force access to a bound address, or use an internal EEPROM/PMIC as a test device. Verify a real response, units, and error handling.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.
