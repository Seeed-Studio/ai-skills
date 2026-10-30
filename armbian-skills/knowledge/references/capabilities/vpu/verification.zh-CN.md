---
schema_version: '1'
id: capability.vpu.verification
kind: capability_guide
applies_to:
  capabilities:
  - vpu
required_refs:
- capability.vpu
- common.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# VPU 验证

按 decode/encode 分别固定 codec/profile/位深/分辨率和输入摘要。检查实际后端、输出可解码、帧数/时长和错误；逐阶段区分 CPU、VPU、缩放与拷贝。工具列出的硬件功能不证明执行成功。
