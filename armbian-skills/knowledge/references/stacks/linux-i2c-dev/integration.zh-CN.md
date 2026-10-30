---
schema_version: '1'
id: stack.linux-i2c-dev.integration
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

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Linux i2c-dev: integration

已有驱动优先使用其业务接口；裸 I2C 按器件 datasheet、运行权限和项目语言绑定选择。处理重复启动、读写方向、数据单位、超时和有限重试。
