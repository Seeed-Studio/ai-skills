---
schema_version: '1'
id: integration.go.guide
kind: integration
applies_to:
  languages:
  - go
required_refs:
- common.project-integration
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.go-cgo
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# go 工程接入

沿用 go.mod/go.sum 和原有 handler/采集模块。区分纯 Go UAPI 绑定、cgo 和既有服务 API；cgo 需要目标 C toolchain、头文件与链接库，不能把 GOARCH 设置等同于完整交叉构建。用 context/关闭通道协调退出，单一 owner 访问硬件，业务 API 读取有时间戳的缓存；处理设备错误和过期状态而非返回伪造正常值。
