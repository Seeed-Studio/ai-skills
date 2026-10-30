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
updated_at: '2026-10-19'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Linux i2c-dev: detection

i2cdetect -l 仅列 adapter；检查 /sys/class/i2c-dev 与已绑定驱动。不要运行无明确器件范围的裸i2cdetect扫描。实际总线编号需现场解析。
