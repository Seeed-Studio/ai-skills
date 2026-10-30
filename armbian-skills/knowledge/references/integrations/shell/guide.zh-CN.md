---
schema_version: '1'
id: integration.shell.guide
kind: integration
applies_to:
  languages:
  - shell
required_refs:
- common.project-integration
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

[English](guide.md) | [简体中文](guide.zh-CN.md)

# shell 工程接入

一次性命令也是应用交付。核对工具本机帮助和版本；libgpiod 1.x/2.x 语法与保持行为不能混用。明确目标、参数、时限、退出码、进程持有/资源释放和断连后状态，输入作为参数处理。短命令无需部署常驻服务；高频业务不强制用 shell 包装。
