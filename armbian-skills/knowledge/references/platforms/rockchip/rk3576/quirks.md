---
schema_version: '1'
id: platform.rockchip.rk3576.quirks
kind: platform_guide
applies_to:
  soc_ids:
  - rockchip.rk3576
required_refs:
- platform.rockchip.rk3576
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-family-config
- source.rknn-project
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](quirks.md) | [简体中文](quirks.zh-CN.md)

# RK3576 software differences

- The referenced host vendor GPU path is Panfrost. Do not overwrite Mesa/EGL with libmali based on an old tutorial.
- A source tree does not prove that the target runs it. Record inspected file SHA256 and check target kernel/DT/packages separately.
- RKNN execution and model conversion are distinct stages. Do not reuse an external RK182x/RKNN3 target configuration for RK3576.
- Check video hardware and framework features separately; bundled FFmpeg may lack the required MPP integration.
- Bindings/native extensions depend on architecture/ABI. Inspect the project before changing its technology stack.
