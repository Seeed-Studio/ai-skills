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

# C/C++ project integration

Check the existing build system, headers, linker, and target sysroot. Use matching kernel UAPI/vendor headers. Define RAII/close paths, error codes, buffers, thread ownership, and cancellation. Do not copy structures from a different ABI. Store interface mappings in project configuration and resolve controller paths from the current target.
