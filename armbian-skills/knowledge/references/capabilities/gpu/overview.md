---
schema_version: '1'
id: capability.gpu
kind: capability
applies_to:
  capabilities:
  - gpu
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

[English](overview.md) | [简体中文](overview.zh-CN.md)

# GPU application development

Verify graphics and compute separately through the actual APIs. Record renderer/provider, desktop or headless context, user/container access, and output. DRM nodes alone do not prove application acceleration.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.
