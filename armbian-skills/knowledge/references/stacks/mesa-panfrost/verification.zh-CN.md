---
schema_version: '1'
id: stack.mesa-panfrost.verification
kind: stack_guide
applies_to:
  capabilities:
  - gpu
  stack_ids:
  - mesa-panfrost
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-kernel-config
- source.mesa-panfrost
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Panfrost kernel + Mesa userspace: verification

使用小型匹配 API 的样例，记录真实 renderer/device 和输出，识别 llvmpipe/软件回退；计算能力独立验证。当前 renderer 与所有 API 未检测。
