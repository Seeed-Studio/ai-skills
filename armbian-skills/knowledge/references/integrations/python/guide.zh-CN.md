---
schema_version: '1'
id: integration.python.guide
kind: integration
applies_to:
  languages:
  - python
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

# python 工程接入

沿用 pyproject/requirements/venv 与现有采集入口。核对原生扩展的架构和系统库版本；语言包能导入不证明设备访问或 ABI 完整。明确文件描述符/请求持有者、context manager/退出、采集线程或异步隔离、超时与旧值状态。先复用原业务 API，不把传感器示例独立于项目交付。
