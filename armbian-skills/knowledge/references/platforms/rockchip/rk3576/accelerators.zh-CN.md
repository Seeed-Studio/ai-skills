---
schema_version: '1'
id: platform.rockchip.rk3576.accelerators
kind: platform_guide
applies_to:
  soc_ids:
  - rockchip.rk3576
required_refs:
- stack.rockchip-rknn
- stack.mesa-panfrost
- stack.rockchip-mpp
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-board-config
- source.local-kernel-config
- source.cached-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](accelerators.md) | [简体中文](accelerators.zh-CN.md)

# RK3576 加速软件栈候选

| 能力 | 候选 stack | 集成与证明 |
|---|---|---|
| NPU | stack.rockchip-rknn | 明确 RK3576 模型、driver/runtime 与语言绑定；固定输入正确且有 NPU 执行证据 |
| GPU 图形 | stack.mesa-panfrost | 确认实际 renderer、EGL/GLES 等 API、桌面/headless 与运行权限 |
| GPU 计算 | 实际 API 另行检测 | 不从图形可用推导 OpenCL/Vulkan 或特定计算框架可用 |
| VPU 解码/编码 | stack.rockchip-mpp | 检查实际 MPP/媒体框架、codec/profile/位深/分辨率与输出 |

不得因 nominal TOPS、config 或工具功能列表报告已支持。集成进已有应用时检查服务/容器真实可访问性，而不只是在 root shell 下运行例子。
