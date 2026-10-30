---
schema_version: '1'
id: stack.linux-gpio-chardev.recovery
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
- stack.linux-gpio-chardev.integration
- stack.linux-gpio-chardev.verification
sources:
- source.linux-gpio-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](recovery.md) | [简体中文](recovery.zh-CN.md)

# GPIO lifetime, exit, and recovery

Request release, direction/configuration restoration, physical voltage, and external-device state are distinct outcomes. `released` or an empty consumer only establishes the absence of that owner, not restoration of the original level/direction.

## Before an operation

Record target, controller identity/local offset, original direction, readable bias/active-low/mux/owner, external circuit, and agreed end value. Unknown fields remain unknown; software configuration does not replace measurement. Keep scope aligned with the user's goal. If an existing service owns a resource, use its API or modify its implementation rather than taking it for recovery.

## Normal completion, cancellation, and failure

Hold the request for the application-defined lifetime and configure initial output atomically where possible. End/cancel values depend on circuit and task; a particular "LOW for 200ms" cleanup is not a universal safe state. Report cleanup errors while attempting release. SIGKILL and power loss cannot execute userspace cleanup. After reconnection, check the original process/request before repeating output.

## Restoring known state

Restore only original settings that are known and still appropriate. Recheck mux/owner and handle races through a real exclusive request. Do not guess unknown direction/bias/mux with extra requests. Restoration can change electrical levels, so assess the external circuit and obtain necessary conditions. Continue code work that does not depend on missing conditions.

Running gpioget once is not a universal restoration method. It requests the line and some versions force input. If `--as-is` preserves direction in the current version, it cannot restore a different direction. Check installed CLI options; gpioget is not passive inventory.

## Acceptance records

Separately record readings during the hold window, exit/signal/release events, restoration actions/final metadata, and whether physical measurements were repeated afterward. Mark a brief cleanup pulse unmeasured when it could not be observed; software readback cannot substitute for waveform evidence. Voltage remains unknown after direction restoration without a new measurement.
