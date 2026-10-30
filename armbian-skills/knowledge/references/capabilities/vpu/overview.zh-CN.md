---
schema_version: '1'
id: capability.vpu
kind: capability
applies_to:
  capabilities:
  - vpu
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

# VPU 应用开发

解码与编码分别确认 codec/profile/level、位深、格式、分辨率及框架接入。记录每段流水线实际后端，验证帧数/时长和输出可解码性，不以软件回退当硬件通过。

未收录平台可继续核对官方接口并做有界测试；关键接线或兼容性未知时，继续离线实现并将相关实机步骤标为未验证。
