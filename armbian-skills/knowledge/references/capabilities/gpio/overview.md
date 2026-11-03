---
schema_version: '1'
id: capability.gpio
kind: capability
applies_to:
  capabilities:
  - gpio
required_refs:
- common.capability-evidence
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-gpio-api
- source.linux-gpio-lifetime
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-11-03'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# GPIO application development

Resolve the user's connector and physical pin using matching board documentation. An unverified line name cannot replace pin-to-net mapping. Locate the current gpiochip and local line, inspect consumer/mux state, and let the actual exclusive request handle ownership races.

Prefer the GPIO character device and an API/libgpiod version matching the installed environment. Use the LED/input subsystem for functions managed there. Configure output direction and initial value together, and distinguish physical high/low from active-low logical values.

The command or daemon must hold the line request for the intended lifetime. After release, userspace no longer guarantees an output level. Fault-safe states require suitable hardware. Software readback alone does not prove external voltage.

References: [Linux GPIO API](https://docs.kernel.org/userspace-api/gpio/chardev.html), [request lifetime](https://docs.kernel.org/userspace-api/gpio/gpio-v2-get-line-ioctl.html).

Before giving wiring/output steps, carry the selected pin's **header-side voltage, SoC-side voltage and translation path** into the answer; do not leave those distinctions only in the pin table. Explain endpoints and polarity using [wiring guidance](../../common/wiring-diagrams.md). An LED working on a supply rail does not establish a GPIO/translator's drive-current budget; a resistor alone is not proof that direct drive is appropriate.

For a brief CLI check, give a version-matched, finite hold and explicit cancellation/release checks from the [bounded GPIO guide](../../recipes/bounded-gpio-command/guide.md). Missing load specifications may block direct LED drive without blocking delivery of a conditional unloaded voltage-check procedure. Do not execute that procedure until the actual wiring, instrument, mux and ownership conditions are confirmed.
