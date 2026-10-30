---
schema_version: '1'
id: capability.vpu.verification
kind: capability_guide
applies_to:
  capabilities:
  - vpu
required_refs:
- capability.vpu
- common.verification
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

[English](verification.md) | [简体中文](verification.zh-CN.md)

# VPU verification

For decode and encode separately, fix codec/profile, bit depth, resolution, and input digest. Check actual backend, decodable output, frame count/duration, and errors. Distinguish CPU, VPU, scaling, and copies by stage. A tool's hardware feature list does not prove execution.
