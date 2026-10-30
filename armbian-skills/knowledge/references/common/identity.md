---
schema_version: '1'
id: common.identity
kind: common
applies_to: {}
required_refs:
- common.capability-evidence
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

[English](identity.md) | [简体中文](identity.zh-CN.md)

# Device identity and platform boundaries

Distinguish the project workspace, build host, and runtime device. Collect facts using an authorized SSH connection, terminal connector, or local terminal. A connection failure does not authorize running target hardware commands on the host.

Exact Device Tree compatible matches identify candidates. User hints and aliases are clues; compare product, revision, and conflicting sources. A matching SoC does not establish carrier routing or electrical conditions. With unknown revision, continue platform research, coding, and functions independent of header pins; do not choose the newest revision's pinout.

The matcher does not fill current facts from old snapshots or authorize outputs from a board ID. GPIO writes require connector, physical numbering/orientation, electrical conditions, reliable SoC-to-controller/line mapping, and current mux/consumer. Pause only operations that depend on missing information.

Refresh affected facts after reconnection or kernel, overlay, user/container, or runtime changes. Record time, target, and source. Do not commit SSH addresses, passwords, user files, or raw captures to shared references.
