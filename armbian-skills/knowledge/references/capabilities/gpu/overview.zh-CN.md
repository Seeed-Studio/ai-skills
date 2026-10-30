---
schema_version: '1'
id: capability.gpu
kind: capability
applies_to:
  capabilities:
  - gpu
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

# GPU 应用开发

按实际 API 分开验证图形和计算能力。记录 renderer/provider、桌面/headless、用户/容器可访问性和输出。不从存在 DRM 节点推导应用已硬件加速。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
