---
schema_version: '1'
id: integration.javascript.guide
kind: integration
applies_to:
  languages:
  - javascript
required_refs:
- common.project-integration
preconditions: []
refines: []
excludes: []
related:
- integration.javascript.rockchip-rknn
sources:
- source.node-child-process
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# JavaScript project integration

Keep package.json, lockfiles, and the actual Node/Electron runtime. Check native addon ABI/architecture; do not assume any npm package works on the target. Isolate blocking I/O with async APIs/workers and serialize resource ownership. When a CLI is necessary, use spawn/execFile argument arrays and shell:false; handle error/close/timeout and the resource-holding process. Do not interpolate user input into a shell or launch a CLI per media frame.

For Rockchip NPU tasks, read [RKNN integration](rockchip-rknn.md). Preserve the user's model and business entry point. Verify numerical results, actual backend, CPU fallback, and lifecycle separately. Missing ready-made JS bindings do not require rewriting the application in Python.
