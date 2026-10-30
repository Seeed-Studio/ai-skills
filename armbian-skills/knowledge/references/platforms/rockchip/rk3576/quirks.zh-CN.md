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

# RK3576 软件差异

- Host 当前 vendor GPU 路径是 Panfrost；不要根据旧教程安装 libmali 来覆盖 Mesa/EGL 文件。
- Source tree 存在不证明目标使用了它；记录所查文件 SHA256，目标需另查 kernel/DT 和实际包。
- RKNN 运行与模型转换属于不同阶段；RK3576 的模型/目标参数不能借用外接 RK182x 的 RKNN3 方案。
- 视频硬件与应用框架功能独立核对；系统自带 FFmpeg 不一定带目标 MPP 接入。
- 语言绑定和 native extension 与架构/ABI 相关，先检查原项目，不强制重写技术栈。
