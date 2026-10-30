---
schema_version: '1'
id: common.project-integration
kind: common
applies_to: {}
required_refs:
- common.identity
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](project-integration.md) | [简体中文](project-integration.zh-CN.md)

# 扩展已有应用或实现新功能

先读取项目约定、入口、依赖/锁文件、已有硬件抽象、配置、测试和部署方式。已有工程沿用语言、架构和业务入口；不因为缺少语言绑定就换语言或交付孤立 demo。

形成与任务规模相符的集成计划：目标与验收条件；原有入口/扩展点；接口及已知/未知条件；资源所有者与数据流；实际运行用户/容器；新增依赖与构建；断连/超时/取消行为；变更、回归与恢复。简单任务可记在会话中，不额外建立批准流程。

按实际条件选择原生库、Linux API、厂商 C API/FFI 或已有服务公开接口。低频管理可调用已有 CLI；实时采集/媒体/推理不要逐帧启动子进程。必要绑定只服务当前工程，不强制用户采用统一 SDK、控制 daemon 或 JSON 协议。

实现要进入原业务链路，保留用户改动。打开/释放和并发所有权明确；阻塞硬件 I/O 与 Web/event loop 分开处理；错误、读数过期、资源忙和超时有可观察结果。新项目才创建必要的源码、依赖和配置。

扩展前保存相关旧功能的可复现结果和代码状态，扩展后通过原入口回归；仅新增测试通过不足以说明旧业务保留。持续操作的生命周期与发起它的短请求分开，明确业务/API取消和应用退出如何终止操作；资源清理完成前仍由原owner持有。硬件不可用时按业务语义降级并公开原因，不无故停止无关业务或伪报硬件成功。

新手从“可以做什么、用哪个接口、要准备什么、如何运行与观察结果”开始。接线/测量等人工动作明确位置与预期，用户报告与 Agent 实测分开；等待必要人工动作时继续离线实现或相关资料工作。

任务记录不要求固定存储协议。跨阶段可在项目约定位置保存：目标、工作区/构建环境、能力证据、产物路径与摘要、代码版本/未提交变更、配置变化、验收结果与恢复。不要包含凭据。

需要用户接线时，按[接线示意图](wiring-diagrams.zh-CN.md)提供排针定位图、逐线连接与接线表；按实际板型与模块调整。
