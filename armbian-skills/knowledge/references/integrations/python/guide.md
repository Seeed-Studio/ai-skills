---
schema_version: '1'
id: integration.python.guide
kind: integration
applies_to:
  languages:
  - python
required_refs:
- common.project-integration
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

[English](guide.md) | [简体中文](guide.zh-CN.md)

# Python project integration

Keep pyproject/requirements/venv and existing collection entry points. Check native-extension architecture and system library versions. Import success does not prove device access or ABI compatibility. Define descriptor/request ownership, context-manager/shutdown paths, collection threads or async isolation, timeouts, and stale-value state. Reuse the original business API instead of delivering a sensor example outside the project.
