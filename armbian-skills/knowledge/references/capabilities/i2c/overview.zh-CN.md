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
updated_at: '2026-11-03'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# I2C 应用开发

核对外部总线、器件型号、供电、电平与地址。优先内核驱动/IIO/hwmon，必要时使用 i2c-dev。不能默认扫描全部总线、强制访问已绑定地址或把内部 EEPROM/PMIC 当测试器件。验证真实响应、数据单位和异常处理。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。

AHT20提出任何事务前，先读[地址、状态与证据规则](aht20.zh-CN.md)。I2C地址加读写位不是payload命令。区分被动元数据、读消息和写读事务；读取器件也需已有器件访问授权。其他芯片可能需要写寄存器指针，按其协议，不套AHT20模式。

快照没有某地址的注册客户端，不证明地址空闲或传感器从未应答。root元数据/工具存在不等于原应用可访问；实际用户/服务/容器未验证时，摘要与正文都保留unknown。状态ACK不是器件身份、校准后测量或电气验收。
