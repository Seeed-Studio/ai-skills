---
schema_version: '1'
id: capability.gpio.verification
kind: capability_guide
applies_to:
  capabilities:
  - gpio
required_refs:
- capability.gpio
- common.verification
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# GPIO 验证

验证初始电平与方向的配置时序，正常保持、到期结束、取消、失败/崩溃和重复启动的行为。GPIO line request 释放后不保证保持电平；kill -9 无法运行用户态清理。将逻辑 active/inactive 与物理高低分别记录，需要安全态时有外部硬件保证。实际申请处理资源竞争，不强制抢占。
