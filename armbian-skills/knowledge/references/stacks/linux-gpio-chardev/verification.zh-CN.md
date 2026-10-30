---
schema_version: '1'
id: stack.linux-gpio-chardev.verification
kind: stack_guide
applies_to:
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs: []
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.cached-vendor-dts
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# GPIO 栈验收

结合已确认的连接器映射、电气、接线和当前资源归属，验证初值、保持、到期、忙/竞争、取消、错误及释放。软件回读只证明API观察，不等于物理电压。使用应用真实用户/容器；root成功不代表普通用户成功。

按[恢复流程](recovery.zh-CN.md)分别检查request释放、方向/配置、仪表电压和外部器件。仅在知道原状态且适合任务时恢复对应字段，不统一拉低或切输入。记录未测量、失败和未知项。
