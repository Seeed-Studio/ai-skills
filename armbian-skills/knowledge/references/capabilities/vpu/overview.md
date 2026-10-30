---
schema_version: '1'
id: capability.vpu
kind: capability
applies_to:
  capabilities:
  - vpu
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

# VPU application development

Check decode and encode separately: codec/profile/level, bit depth, format, resolution, and framework integration. Record each pipeline stage's actual backend; verify frame count/duration and decodable output. Software fallback does not count as a hardware pass.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark dependent hardware steps unverified.
