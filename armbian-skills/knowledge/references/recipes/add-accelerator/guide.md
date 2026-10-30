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

# Adding acceleration to an existing application

Preserve project language and inference/media entry points. Check model/input, target driver/runtime, and ABI. Establish a bounded backend example, then integrate loading, preprocessing, execution, errors, and release into the project. Verify correct output, actual backend, missing dependencies/fallback, and old behavior. A standalone benchmark does not replace integration. GPU/VPU tasks require their own operations/APIs rather than inheriting the NPU stack.
