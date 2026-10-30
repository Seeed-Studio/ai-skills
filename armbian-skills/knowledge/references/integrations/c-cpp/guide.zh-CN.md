---
schema_version: '1'
id: integration.c-cpp.guide
kind: integration
applies_to:
  languages:
  - c-cpp
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

# c-cpp 工程接入

检查现有构建系统、头文件、链接器与目标 sysroot。用匹配内核 UAPI/厂商头文件，明确 RAII/关闭路径、错误码、缓冲区、线程归属与取消，避免复制不同 ABI 的结构体。接口映射保存在项目配置，控制器路径由当前目标解析。
