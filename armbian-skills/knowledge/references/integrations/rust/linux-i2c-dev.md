---
schema_version: '1'
id: integration.rust.linux-i2c-dev
kind: integration
applies_to:
  languages:
  - rust
  capabilities:
  - i2c
  stack_ids:
  - linux-i2c-dev
required_refs:
- integration.rust.guide
- stack.linux-i2c-dev
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.linux-i2c-api
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](linux-i2c-dev.md) | [简体中文](linux-i2c-dev.zh-CN.md)

# Rust / linux-i2c-dev

Prefer an existing kernel device driver's public interface. Raw i2c-dev access must match the sensor protocol, adapter capabilities, address, and combined-transaction semantics. Implement only transactions needed by the confirmed device, without scanning internal buses. Preserve errors and stale timestamps after failed/timed-out reads; never present an old value as fresh.

Check the chosen library and pinned version in the actual project. This guide defines integration and acceptance constraints, not certification of a language binding. Configure the currently resolved device identity and resource/address; do not hardcode another board's nodes into generic source.
