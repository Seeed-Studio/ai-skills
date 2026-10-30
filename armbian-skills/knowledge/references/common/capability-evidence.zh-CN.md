---
schema_version: '1'
id: common.capability-evidence
kind: common
applies_to: {}
required_refs: []
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

[English](capability-evidence.md) | [简体中文](capability-evidence.zh-CN.md)

# 四层能力与证据

分别报告硬件/接口、系统就绪、应用可访问、功能实测。使用 available、needs-setup、busy、unsupported、unknown；未检测/未测试显式说明。来源可以是官方硬件资料、Host 源码、运行时或测量，不能相互替代。

绑定事实到设备、版本、采集时间与任务条件。设备重启、driver/runtime/overlay、运行用户、容器或模型改变后刷新相关证据。知识缺失不是不兼容；条件可判断时开展有界最小测试，结果先作为项目证据，不自动扩大支持声明。
