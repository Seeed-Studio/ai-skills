---
schema_version: '1'
id: common.platform-onboarding
kind: common
applies_to: {}
required_refs:
- common.reference-matching
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](platform-onboarding.md) | [简体中文](platform-onboarding.zh-CN.md)

# Adding platforms and maintaining references

Reuse the workflow modules in armbian-hardware rather than cloning entry points per board. Add stable platform/board IDs and compatible candidates with sources, separating SoC and carrier. Do not invent a pinout for an unknown revision. For a new image, update stack/compatibility information rather than copying physical pin data.

Read the metadata schemas and declare explicit `applies_to` conditions. Required dependencies and `refines` must be acyclic; navigation may be bidirectional. Recipes and language guides cannot remove protected electrical/pin restrictions. Add a stack for a distinct software API, not simply because a SoC name suggests a runtime.

Test exact matches, missing fields, alias ambiguity, revision conflicts, exclusions, and RK35xx board/SoC differences. Then use an actual platform application to check discovery, implementation/integration, deployment, physical function, and lifecycle. Mark hardware acceptance pending when no device is available; fixtures are not physical passes.

Record sources/versions/digests, maintainers, verification scope, and invalidation conditions. Publish reviewed static knowledge only; validation records, captures, and credentials stay in the project. Run host `refresh_catalog.py`, tests, and `build_skills.py`; regenerate the self-contained armbian-hardware package and check self-contained references/digests.

English `.md` files are canonical. Adjacent `.zh-CN.md` files are independent Chinese translations with the same reference ID and applicability metadata, not additional catalog entries. Keep both versions consistent; indexes resolve the canonical file, and package digests cover both languages. Do not translate device identifiers, pin names, schema keys, or source artifacts.
