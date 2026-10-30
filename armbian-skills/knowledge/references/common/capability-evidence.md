---
schema_version: '1'
id: common.capability-evidence
kind: common
applies_to: {}
required_refs: []
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

[English](capability-evidence.md) | [简体中文](capability-evidence.zh-CN.md)

# Four capability layers and their evidence

Report hardware/interfaces, system readiness, application access, and functional hardware results separately. Use `available`, `needs-setup`, `busy`, `unsupported`, and `unknown`; explicitly identify uninspected or untested items. Official hardware documentation, host source, runtime observations, and measurements are different evidence types and cannot replace one another.

Bind facts to the device, version, collection time, and task conditions. Refresh affected evidence after reboot or changes to driver/runtime/overlay, runtime user, container, or model. Missing knowledge is not incompatibility. When conditions are established, run a minimal bounded test; keep results in the project first without automatically expanding support claims.
