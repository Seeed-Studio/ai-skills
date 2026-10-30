---
schema_version: '1'
id: common.deployment
kind: common
applies_to: {}
required_refs:
- common.linux-device-access
- common.capability-evidence
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

[English](deployment.md) | [简体中文](deployment.zh-CN.md)

# 部署、运行身份与恢复

沿用应用现有部署方式，明确工作区、构建环境、目标设备和部署目录。一次性命令无需变成服务。先确认产物源码版本/摘要、目标架构、动态链接器及库 ABI，再传送到目标暂存路径；Host 构建成功不证明目标可运行。

修改前保存受影响版本与配置和可执行恢复步骤。只替换本项目拥有的文件，保留现有项目配置及用户改动；先准备待部署版本和检查，再按已有授权实施。权限按具体设备/用户配置，不把全部节点公开可写或给予任意免密 root。

服务按目标实际管理器配置：运行用户、WorkingDirectory、环境/依赖、就绪、日志、停止超时、资源释放与重启策略。检查 hardening 对设备和库访问的实际影响，不能机械套用会隐藏设备的 PrivateDevices。硬件输出在崩溃重启时的重复行为要明确。

启动后分别检查进程、管理器 running、业务 ready 和硬件功能；只有 running 不算完成。要求开机运行时验证对应启动行为，重启整机仅在任务需要且已授权时执行。不要为取消单任务停止共享服务。

SSH 断开或超时后先查原进程/日志/产物和设备状态，再决定是否重试。结果无法查询时报告不确定；不能把附加 request ID 当作去重保证。保留取消与回滚记录，不能用“回滚了配置”代替外部硬件恢复证据。
