---
schema_version: '1'
id: stack.rockchip-rknn.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Rockchip RKNPU and compatible RKNN runtime: verification

Fix model/input and correctness criteria. Retain actual runtime/device execution evidence and separate end-to-end/inference timings. Establish current kernel driver, userspace runtime, binding, model, and functional readiness on the target; these are not supplied by static profiles.

Use these separate acceptance checks for the user's own program:

| Check | Evidence |
| --- | --- |
| Application access | The actual service user/container loads the recorded runtime and can access the SDK's actual DRM/device node; root-shell inventory or a separate SDK demo does not establish this |
| Output correctness | Run fixed inputs through that program with recorded preprocessing, compare its outputs with known expectations and error bounds |
| Compute attribution | Correlate that run with version-supported profiling/tracing or execution-backend output; inspect compute Target/cycles where supported, accounting for graph fusion/optimization |

Runtime availability and a converted model are prerequisites, not an acceptance result. A minimal-proof checklist or closing summary must retain all three checks; do not replace them with "install runtime + convert model + observe load". Unsupported attribution queries leave that evidence unresolved; they do not require every operator row or a particular API to exist. Distinguish CPU preprocessing/I/O from whole-model CPU fallback and record explicit fallback separately.

Counters are optional supporting observations: zero can miss short work; positive load can come from another process. Neither load nor an open device FD establishes correct output and compute attribution by itself. After completion/error/cancellation inspect contexts/processes/FDs; power state is not proof of release.
