---
schema_version: '1'
id: stack.linux-gpio-chardev.integration
kind: stack_guide
applies_to:
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs: []
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources:
- source.cached-vendor-dts
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](integration.md) | [简体中文](integration.zh-CN.md)

# GPIO application integration

Keep project language and runtime form. Select native APIs, bindings, FFI, or an existing interface for the actual kernel UAPI/libgpiod version. CLI arguments must match installed tools. Go/Rust/JS need not pass through a common CLI wrapper.

Define request open/hold/close, initial value, concurrency, timeout, cancellation, and errors. Set the initial output atomically with the request where possible. End values depend on the circuit; closing a request guarantees neither level nor direction. If restoration is required, record known original state and verify results using [lifecycle and recovery](recovery.md).

Integrate with existing service/event loops without blocking business behavior. Preflight does not eliminate races: handle request errors without seizing kernel/shared resources. Resolve paths from the current controller identity, not fixed chip numbers or unverified PIN labels.
