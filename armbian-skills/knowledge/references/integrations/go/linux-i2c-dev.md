---
schema_version: '1'
id: integration.go.linux-i2c-dev
kind: integration
applies_to:
  languages:
  - go
  capabilities:
  - i2c
  stack_ids:
  - linux-i2c-dev
required_refs:
- integration.go.guide
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
updated_at: '2026-10-20'
---

[English](linux-i2c-dev.md) | [简体中文](linux-i2c-dev.zh-CN.md)

# Go / linux-i2c-dev

Prefer an existing kernel device driver's public interface. Raw i2c-dev access must match the sensor protocol, adapter capabilities, address, and combined-transaction semantics. Implement only transactions needed by the confirmed device, without scanning internal buses. Preserve errors and stale timestamps after failed/timed-out reads; never present an old value as fresh.

Check the actual library and pinned version; no arbitrary third-party binding is certified here. Configure the currently resolved adapter/controller and device address, not another board's node. An I2C address is not a GPIO line offset. Avoid I2C_SLAVE FORCE. A cooperative process lock is not whole-bus exclusivity and cannot replace kernel address-ownership checks.

Integrate collection with the original service API and retain old behavior. HTTP handlers read a cache; do not hold its lock across hardware I/O. On failure, retain the last successful data and original timestamp/sequence while explicitly reporting errors/staleness. Use monotonic time for freshness and record UTC clock calibration separately. Go context does not automatically interrupt blocked kernel I2C I/O. If deadlines matter, choose a suitable controlled worker process or driver/project mechanism. Do not start another retry until the old I/O owner has exited. Userspace cannot guarantee immediate termination of uninterruptible kernel I/O.

A datasheet may use eight-bit wire addresses while the API takes a seven-bit address. For AHT20, 0x71 is the read address for 0x38, not a payload byte to write again. Do not blindly concatenate short reads with io.ReadFull: another read may start a new transaction. Combined transactions/repeated starts depend on the actual device.
