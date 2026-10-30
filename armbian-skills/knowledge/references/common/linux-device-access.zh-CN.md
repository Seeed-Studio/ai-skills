---
schema_version: '1'
id: common.linux-device-access
kind: common
applies_to: {}
required_refs:
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

[English](linux-device-access.md) | [简体中文](linux-device-access.zh-CN.md)

# 应用访问检查

采集系统身份、运行用户、节点权限、服务配置与容器映射。使用标准 Linux 接口或项目已有业务 API；资源被驱动/应用持有时不旁路抢占。

只读 inventory 不执行 GPIO 请求/输出、I2C 扫描、原始寄存器访问、服务重启、overlay 变更、GPU benchmark 或模型推理。应用功能测试另行定义输入、时限、结束条件和验收。

本知识库提供的 probe_device.py 无需凭据文件；SSH 在操作者终端完成认证，输出写在 Host。该 probe 只查看环境，不作为已实测的功能报告。
