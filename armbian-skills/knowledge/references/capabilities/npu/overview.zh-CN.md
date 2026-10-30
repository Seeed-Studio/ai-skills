---
schema_version: '1'
id: capability.npu
kind: capability
applies_to:
  capabilities:
  - npu
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

# NPU 应用开发

识别目标、driver/runtime、模型目标与输入 shape/dtype/量化、预处理和后处理。复用项目语言或最小桥接。固定输入验证正确性与实际硬件后端；CPU fallback 单独报告。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
