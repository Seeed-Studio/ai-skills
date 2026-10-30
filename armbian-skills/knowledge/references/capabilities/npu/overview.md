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

# NPU application development

Identify the target, driver/runtime, model target, input shape/dtype/quantization, and preprocessing/postprocessing. Keep the project's language or use a minimal bridge. Verify correctness and actual hardware execution with fixed inputs; report CPU fallback separately.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.
