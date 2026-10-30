---
schema_version: '1'
id: integration.javascript.rockchip-rknn
kind: integration
applies_to:
  languages:
  - javascript
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs:
- integration.javascript.guide
- stack.rockchip-rknn
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.node-child-process
- source.rknn-v232-sdk
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](rockchip-rknn.md) | [简体中文](rockchip-rknn.zh-CN.md)

# Integrating Rockchip RKNN with JavaScript

Keep original JS entry points, score/error semantics, packages, and tests. RKNN C/C++ and Python APIs do not require changing the application's language. Choose an existing binding, N-API addon, FFI, existing service API, or bounded native worker as appropriate. Check Node ABI/architecture, C headers/runtime, and target model; external processes are not a default per-frame media solution.

Keep a synchronous CPU business interface if needed and add an explicit async hardware path. Do not block the event loop with synchronous spawn. For a process bridge, use argument arrays, shell=false, bounded input/output, timeout/AbortSignal, and error/close handling. Distinguish requesting termination from actual process exit; do not overlap retries while the old owner remains. SIGKILL or uninterruptible kernel I/O cannot guarantee userspace destroy or immediate stop.

Pin model digest, target SoC, layout/shape/dtype, quantization, and preprocessing. Original ONNX attributes are not converted RKNN attributes. Query the runtime and submit actual formats, explaining pass_through and output conversion. A qnt_type enum alone does not establish INT8: inspect dtype, build settings, and field semantics. Channels/layouts may require real reordering; the single-channel case of identical contiguous storage cannot be generalized to RGB.

A successful call, node existence, or the word "NPU" is insufficient. Check known inputs/expected output, per-operator Target/computation cycles, and actual NPU device correlation. Record initial/final CPU regression, missing runtime/model, wrong target, and cancellation/release separately. Explicit fallback must return backend=cpu and its reason; baseline/fallback results are not NPU passes. CPU input/output conversion does not mean whole-model CPU fallback; describe stages separately.

The runtime may open a primary DRM card instead of a render node. Correlate both through sysfs and actual file descriptors rather than hardcoding card2/renderD130. Root-shell inventory does not establish service/container access; check SDK-required nodes as the final runtime user.
