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
updated_at: '2026-10-19'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# I2C 应用开发

核对外部总线、器件型号、供电、电平与地址。优先内核驱动/IIO/hwmon，必要时使用 i2c-dev。不能默认扫描全部总线、强制访问已绑定地址或把内部 EEPROM/PMIC 当测试器件。验证真实响应、数据单位和异常处理。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
