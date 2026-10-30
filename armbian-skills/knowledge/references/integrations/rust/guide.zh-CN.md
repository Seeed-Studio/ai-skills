---
schema_version: '1'
id: integration.rust.guide
kind: integration
applies_to:
  languages:
  - rust
required_refs:
- common.project-integration
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.rust-ffi
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# rust 工程接入

保留 Cargo.toml/Cargo.lock、edition 和当前异步运行时。先检查项目已有硬件 crate 和目标 Linux ABI；没有可验证绑定时评估厂商 C API/最小 FFI，并明确 unsafe 边界、指针/缓冲区有效期、线程安全与 Drop。阻塞 I/O 不占用异步执行线程；取消先通知持有硬件的任务再释放。交叉编译核对 target triple、sysroot 和动态库，不能只更改 --target。
