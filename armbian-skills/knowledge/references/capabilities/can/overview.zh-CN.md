---
schema_version: '1'
id: capability.can
kind: capability
applies_to:
  capabilities:
  - can
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-can
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# CAN 应用接入

区分控制器 TX/RX 与收发器后的 CAN_H/CAN_L，确认收发器、终端和测试网络。依据当前驱动选择 SocketCAN 等接口，明确 bitrate、帧格式、过滤和 bus-off 恢复。发送会影响总线；按任务范围测试真实对端，软件虚拟 CAN 结果不算物理验收。
