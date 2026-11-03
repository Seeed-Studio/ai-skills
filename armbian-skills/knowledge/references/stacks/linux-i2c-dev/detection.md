---
schema_version: '1'
id: stack.linux-i2c-dev.detection
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
updated_at: '2026-11-03'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Linux i2c-dev: detection

`i2cdetect -l` lists adapters only. Inspect `/sys/class/i2c-dev` and bound drivers. Do not perform an unrestricted i2cdetect scan. Resolve bus numbering on the current target.

Adapter/node enumeration is metadata; `i2ctransfer` performs real bus I/O. Select the 7-bit slave address separately from the message payload: Linux handles the address and direction on the wire. Do not convert an 8-bit read address from a timing diagram into an extra written byte. For AHT20 use the [specific protocol rules](../../capabilities/i2c/aht20.md); do not infer its status request from the phrase "send 0x71" alone. A write message followed by a read is a write/read transaction, not read-only discovery.
