---
schema_version: '1'
id: stack.rockchip-rknn.integration
kind: stack_guide
applies_to:
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-kernel-config
- source.cached-vendor-dts
- source.rknn-project
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-30'
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Rockchip RKNPU and compatible RKNN runtime: integration

Check current driver/runtime and model target, then choose an existing binding, C ABI/FFI, or service API in the user's language. Treat conversion, calibration, and execution separately; do not directly reuse an external RK182x example.

Use explicit official tags/file digests. Record conversion Toolkit version, target SoC, actual runtime/header/driver, and application architecture. Master/latest is not the installed version. Preserve existing models/bindings; an example version is not a future compatibility whitelist.

Choose the dependency branch from the actual application environment:

| Evidence | Runtime state | Next step |
| --- | --- | --- |
| No package/cache entry; application paths/environment uninspected | unknown | Locate the application's configured/loaded runtime; do not require installation |
| Application runtime found | identified, compatibility/access still to check | Reuse it and record its path/version and actual load result |
| Confirmed missing dependency or unresolved load in that application environment | needs-setup for that dependency/load condition | Supply a compatible task-local dependency or fix its lookup/access; replacing the driver is not implied |

Keep the opening conclusion, state table and proposed actions at the same evidence level. A later caveat about unsearched private libraries cannot justify first declaring the runtime absent. If the application/model is not yet supplied, describe the missing inputs and conditional route rather than assuming installation is necessary. Choose version-supported backend evidence for the bounded run; a sampled load increase is optional supporting evidence, not a condition every valid inference must satisfy.

Conclusion phrasing, side by side: the opening never states cross-source verdicts like "what's really missing is the userspace runtime" or "the board has no runtime". Write instead: "the kernel side is confirmed (driver bound); the userspace runtime was not found in the checked sources <list them>; whether it is missing depends on checking the application's private paths/containers/SDK directories". Express the runtime-install step in check-first order — search the application's real environment, install only once absence is confirmed — never as an unconditional to-do or "the only thing to add". Pair a runtime with the driver per the pairing stated in that driver version's release documentation; "a newer version will do" is not a pairing statement. Name SDK perf/profiling entry points only as they exist in the installed version, never from memory.

Query actual input/output counts, shape/layout/dtype instead of filling RKNN inputs from original ONNX attributes. Define pass_through, normalization, and output-float conversion. Preserve business entry points and use the language's async lifecycle for persistent work. Release outputs/context, and verify actual owner exit after errors/cancellation.
