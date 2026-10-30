---
schema_version: '1'
id: integration.go.guide
kind: integration
applies_to:
  languages:
  - go
required_refs:
- common.project-integration
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.go-cgo
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# Go project integration

Keep go.mod/go.sum and existing handlers/collectors. Distinguish pure-Go UAPI bindings, cgo, and existing service APIs. cgo requires target C tools, headers, and libraries; setting GOARCH alone is not a complete cross-build. Coordinate shutdown through contexts/close channels. Use one hardware owner and timestamped caches for business APIs; expose device errors and stale state rather than fabricated normal values.
