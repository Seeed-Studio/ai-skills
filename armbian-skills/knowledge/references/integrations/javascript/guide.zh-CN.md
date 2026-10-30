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

# javascript 工程接入

保留 package.json、锁文件和 Node/Electron 等实际运行环境。核对 native addon ABI/架构，不认为任意 npm 包在目标可用。用异步 API/worker 隔离阻塞 I/O，串行管理硬件资源。确需调用 CLI 时使用 spawn/execFile 的参数数组和 shell:false，处理 error/close/timeout 与持有资源的进程；不要拼接用户输入到 shell，不为每个媒体帧启动 CLI。

Rockchip NPU任务按需读[RKNN接入](rockchip-rknn.zh-CN.md)，保留用户模型与原业务入口，分别验证模型数值、真实计算后端、CPU回退及生命周期；没有现成JS绑定不意味着必须改写成Python。
