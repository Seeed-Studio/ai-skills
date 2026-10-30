---
schema_version: '1'
id: capability.uart
kind: capability
applies_to:
  capabilities:
  - uart
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

# UART 应用开发

核对连接器、TTL/RS232/RS485 标准、波特率与协议，确认不是 console/getty 或其他应用正在使用的端口。先有界接收，再按需求发送；回环或对端响应才证明通信。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
