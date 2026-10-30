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

# Rust project integration

Preserve Cargo.toml/Cargo.lock, edition, and async runtime. Inspect existing hardware crates and target Linux ABI first. Without a verified binding, assess a vendor C API/minimal FFI, defining unsafe boundaries, pointer/buffer lifetimes, thread safety, and Drop. Keep blocking I/O off async executor threads. Notify the hardware-owning task before cancellation/release. Cross-builds require the target triple, sysroot, and dynamic libraries, not merely changing --target.
