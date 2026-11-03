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
updated_at: '2026-11-03'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# I2C application development

Confirm the external bus, device model, supply, signal levels, and address. Prefer a kernel driver or IIO/hwmon interface; use i2c-dev when needed. Do not scan every bus by default, force access to a bound address, or use an internal EEPROM/PMIC as a test device. Verify a real response, units, and error handling.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.

For AHT20, read [its address/status and evidence rules](aht20.md) before suggesting any transaction. An I2C address plus R/W bit is not a payload command. Distinguish passive metadata, a read message, and a write/read transaction; even a device read needs authorized device access. Other chips may need register-pointer writes: follow that chip's protocol, not the AHT20 pattern.

A snapshot with no registered client at an address does not prove it is free or that a sensor has never replied. Root metadata/tool availability is not the existing application's access. Keep that access unknown in the summary as well as the detail until tested for the actual user/service/container. A status ACK is not sensor identification, calibrated measurement or electrical acceptance.
