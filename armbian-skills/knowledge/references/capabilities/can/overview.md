---
schema_version: '1'
id: capability.can
kind: capability
applies_to:
  capabilities:
  - can
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-can
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# CAN application integration

Distinguish controller TX/RX signals from CAN_H/CAN_L after a transceiver. Confirm the transceiver, termination, and test network. Select an interface such as SocketCAN based on the current driver; specify bitrate, frame format, filters, and bus-off recovery. Sending affects the bus, so test a real peer within the task scope. Virtual CAN results do not constitute physical acceptance.
