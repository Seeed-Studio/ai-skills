---
schema_version: '1'
id: integration.rust.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - rust
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.rust.guide
- stack.linux-gpio-chardev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# Rust / linux-gpio-chardev

Determine whether the project uses the kernel GPIO UAPI or libgpiod, checking their ABIs and binding versions separately. One owner must hold the request until expiry/cancellation. Configure direction and initial value together; report busy as a business error rather than forcibly taking ownership.

OwnedFd/Drop can close a request, but restoration and physical state need explicit design. Use an explicit finish path for normal/canceled completion when restoration errors must be reported. Drop supplements error/unwind release; it cannot guarantee cleanup after SIGKILL or power loss. Attempt subsequent restoration/release even if an earlier cleanup step fails.

Limit handwritten UAPI unsafe code to valid repr(C) structures and FFI calls with valid descriptors. Check layout, offsets, ioctls, and libc linkage against the target architecture/headers. A layout checked for Linux x86_64/aarch64 is not proof for another architecture. Other projects may choose appropriate crates/FFI rather than copying a specific implementation.

Signal handlers notify the owner; restoration/release happens in normal control flow, without file I/O/allocation in the handler. Verify atomic initial values, real exclusive contention, known original direction, and active-low semantics separately. Label readback phases and distinguish manual observation windows from default command duration. An inspect command must not silently request a line as a "read-only" check.
