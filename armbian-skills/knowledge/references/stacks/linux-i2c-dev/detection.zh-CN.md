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

i2cdetect -l 仅列 adapter；检查 /sys/class/i2c-dev 与已绑定驱动。不要运行无明确器件范围的裸i2cdetect扫描。实际总线编号需现场解析。

适配器/节点枚举是元数据，`i2ctransfer` 是实际总线I/O。七位从地址与消息payload分开指定，线上地址与方向由Linux处理；不把时序图里的八位读地址变成额外写入字节。AHT20按[专用协议规则](../../capabilities/i2c/aht20.zh-CN.md)，不能只凭“发送0x71”字样推断状态事务。先写后读属于写读事务，不是只读发现。
