---
schema_version: '1'
id: integration.go.linux-gpio-chardev
kind: integration
applies_to:
  languages:
  - go
  capabilities:
  - gpio
  stack_ids:
  - linux-gpio-chardev
required_refs:
- integration.go.guide
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
updated_at: '2026-10-19'
---

[English](linux-gpio-chardev.md) | [简体中文](linux-gpio-chardev.zh-CN.md)

# Go / linux-gpio-chardev

Determine whether the project uses the kernel GPIO UAPI or libgpiod, checking their ABIs and binding versions separately. One owner must hold the request until expiry/cancellation. Configure direction and initial value together; report busy as a business error rather than forcibly taking ownership.

## Integrating existing business behavior

Preserve original modules, entry points, and tests. Give the new hardware path configuration switches and explicit errors. When access is unavailable, degrade according to business requirements while preserving independent health/sample functions. Do not turn every initialization failure into whole-service failure or claim success for business behavior that requires working hardware.

For persistent work started by a short HTTP request, do not blindly inherit a request context that is canceled when its handler returns. Manage bounded work through the application lifecycle, with an operation ID and cancellation entry point; shutdown cancels and waits for cleanup. A short synchronous operation can still use request context without a mandatory background-job protocol.

Keep resource ownership until restoration/release completes; cleanup remains busy. Handle actual request races as well as preflight. Distinguish starting, holding, completed, canceled, and cleanup-failed states. Label the phase of software readback; an initial value is not continuous measurement. Restore only a known state suitable for the circuit; see [recovery](../../stacks/linux-gpio-chardev/recovery.md).

If defining ioctl structures directly in Go, compare sizes, alignment, offsets, and request numbers against target C headers. Validate other architectures and metadata formats separately; one board's pinmux debug index is not a portable rule.

Check original business behavior before/during/after the operation, same-instance and external-owner conflicts, API cancellation, shutdown, unavailable hardware, and the actual runtime user. A pinmux preflight rejection does not establish the result of a device ioctl permission check. Instruments separately establish physical voltage; see [GPIO verification](../../stacks/linux-gpio-chardev/verification.md).
