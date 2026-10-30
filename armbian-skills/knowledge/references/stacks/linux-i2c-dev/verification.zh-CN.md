---
schema_version: '1'
id: stack.linux-i2c-dev.verification
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
updated_at: '2026-10-20'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Linux i2c-dev: verification

需要指定外部器件和确认接线；按器件协议检查响应、数据转换、拔除处理与原业务回归。总线编号本身不证明外部/内部或独占；先追踪排针、控制器、转换/上拉、共线器件及当前owner，不扫描共享总线或强制访问驱动地址。
