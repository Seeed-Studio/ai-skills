---
schema_version: '1'
id: capability.npu.verification
kind: capability_guide
applies_to:
  capabilities:
  - npu
required_refs:
- capability.npu
- common.verification
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# NPU verification

Pin the model digest/target, input shape/layout/dtype, quantization, and preprocessing. Compare known inputs against expected results. Record driver/runtime, actual execution device/backend, and the language bridge ABI. A host example does not replace testing the actual service/container; record CPU fallback separately.

Keep original ONNX attributes separate from runtime attributes. Query the latter before choosing layout/conversion; a quantization enum alone does not establish dtype or data interpretation. SDK success can coexist with conversion errors, so inspect logs and known numerical results. The word "NPU" is not execution evidence: correlate the actual application/runtime/device with version-supported profiling or tracing. Where available, inspect compute Target/cycles for the compiled graph; account for fused/optimized nodes and unsupported queries instead of requiring every operator to have positive NPU cycles. Explain CPU I/O glue or preprocessing separately from whole-model CPU fallback. Sampled load is supporting evidence, not a mandatory positive sample or proof of which process ran.

Scope "not found" to the sources actually checked: no runtime in standard library paths, package caches, or the pip list supports only "not found in those sources". While private install paths, SDK directories, containers, or another user's environment are unchecked, keep the conclusion "not found; may exist in unchecked locations" — never "the board has no runtime" or a claim that it is the only missing piece, and do not turn installing some package into a mandatory step from that. Record the list of sources checked and phrase absence per source scope. The step order for adding a runtime is "search the application's real environment (venv/rpath/container image) first, install only once absence is confirmed": the search is step one, not the install; when recommending an install, pin the tag documented as paired with that driver version's release notes and include a checksum; close with per-source-scope status, never cross-source summaries like "the runtime is blank".

Collection from a root or host session does not prove the actual application can access the NPU: a different user, container, or service may face different device nodes, library paths, and permissions; verify application access inside the application's real runtime environment. Keep load sampling two-sided: a short task can be missed entirely, so failing to sample a non-zero load does not imply "running on CPU"; an unchanged load within a sampling window is also only supporting evidence. Attribution requires cross-checking with version-supported profile/tracing or execution-backend output; never state a definite fallback from sampling alone.
