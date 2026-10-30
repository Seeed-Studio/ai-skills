---
schema_version: '1'
kind: stack_guide
applies_to:
  capabilities:
  - gpu
  soc_ids:
  - rockchip.rk3588
  stack_ids:
  - mesa-panthor
required_refs:
- stack.mesa-panthor
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-rk3588-board
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
id: stack.mesa-panthor.integration
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# Panthor / Mesa integration

沿用项目图形/计算框架，按实际 EGL/GLES/Vulkan 等 API、headless/桌面和用户/容器环境选择接入。Panthor 驱动绑定不保证所有 Mesa API 或计算框架可用；安装/切换图形栈要明确兼容性、影响和恢复。
