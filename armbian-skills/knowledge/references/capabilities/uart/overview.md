---
schema_version: '1'
id: capability.uart
kind: capability
applies_to:
  capabilities:
  - uart
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

# UART application development

Confirm the connector, TTL/RS232/RS485 electrical standard, baud rate, and protocol. Check that the port is not a console/getty or owned by another application. Start with bounded reception, then transmit as required. A loopback or peer response establishes communication.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.
