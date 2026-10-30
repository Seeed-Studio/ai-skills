---
schema_version: '1'
id: capability.pwm
kind: capability
applies_to:
  capabilities:
  - pwm
required_refs:
- common.linux-device-access
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-pwm
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# PWM application integration

Identify the actual provider/channel, connector electrical conditions, and owner. Use the PWM API available on the target. Do not take system resources such as thermal fans or backlights. Record period/duty/polarity and startup, stop, and failure behavior. Software configuration readback does not establish a waveform; measure frequency and duty cycle. Do not guarantee the level after disable without evidence.

Documented pinmux alternatives are candidates, not free, enabled or routed target channels. Missing pwmchip nodes do not identify the cause or prove that an overlay alone will make a channel usable. A requested/enabled pwm-fan proves software ownership, not that a fan is installed or rotating; use tachometer or explicit physical observation for that claim.

For sysfs, period and duty_cycle are in nanoseconds: 50Hz is 20,000,000ns and 1–2ms pulses are 1,000,000–2,000,000ns. This calculation selects no actual channel. External supply and common ground do not establish signal-threshold or translator/load compatibility; check the actual component specifications before offering a drive connection.
