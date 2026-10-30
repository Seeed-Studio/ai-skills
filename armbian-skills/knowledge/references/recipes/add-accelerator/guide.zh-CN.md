---
schema_version: '1'
id: recipe.add-accelerator.guide
kind: recipe_guide
applies_to:
  capabilities:
  - npu
  operations:
  - npu.infer
required_refs:
- recipe.add-accelerator
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

[English](guide.md) | [简体中文](guide.zh-CN.md)

# 给已有应用接入加速

沿用项目语言和推理/媒体业务入口，核对模型/输入、目标 driver/runtime/ABI。先建立有界后端样例，再将加载、预处理、执行、错误和释放接入原项目。验收输出正确性、真实后端、依赖缺失/回退和原功能回归；不以独立 benchmark 代替集成。GPU/VPU 应替换为对应 operation 与 API，不能继承 NPU 软件栈。
