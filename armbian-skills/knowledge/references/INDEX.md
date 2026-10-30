---
schema_version: '1'
id: references.index
kind: index
applies_to: {}
required_refs:
- common.identity
- common.reference-matching
- common.project-integration
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

[English](INDEX.md) | [简体中文](INDEX.zh-CN.md)

# Multi-platform Armbian hardware application references

This collection provides shared workflows and static hardware, source, and software-stack references. Current board profiles cover reComputer RK3576/RK3588 DevKit. Reference applicability does not establish current availability or authorize output: check hardware/interfaces, system readiness, actual application access, and functional results for each task.

| Task | Read |
|---|---|
| Help the user wire or measure hardware | [Wiring diagrams](common/wiring-diagrams.md), exact board/revision and peripheral data |
| Discover hardware and explain interfaces | [Identity](common/identity.md), [four evidence layers](common/capability-evidence.md), matching board/platform and capability |
| Extend existing applications or help beginners | [Project integration](common/project-integration.md), actual stack, language integration, applicable recipe |
| Build, deploy, or maintain services | [Deployment](common/deployment.md), [device access](common/linux-device-access.md), project stack/integration |
| Verify or diagnose | [Acceptance methods](common/verification.md), capability and stack verification |

## Board profiles

- [RK3576 full-system DevKit](boards/seeed/recomputer-rk3576-devkit/overview.md): official 40-pin labels, schematic/SoC mapping, incorrect Linux-label differences, overlay candidates, and software stacks.
- [RK3588 full-system DevKit](boards/seeed/recomputer-rk3588-devkit/overview.md): exact identity rules, full 40 V1.0 J10 documentary mapping (pins23/40 share one net), and stack candidates.
- [Source registry](sources/index.yaml): official hardware/API documentation and versioned source evidence. An unlisted combination is not necessarily unsupported.

## Matching and directory roles

Run `python3 scripts/armbian.py info` for package version, then prepare current facts using the [matching contract](common/reference-matching.md), then run scripts/armbian.py match. Python 3.9+ standard library is sufficient; catalog.json/catalog.yaml share the same source.

The index records applicability, file digests, required dependencies, and navigation/source links by ID. Dimensions use AND, alternatives within a dimension use OR, missing facts remain unknown, and ambiguity is not resolved by choosing the first item. Required/refinement dependencies are acyclic; navigation can be bidirectional. Refinements are not automatically merged.

common covers shared workflows; capabilities covers interface semantics; platforms covers SoCs; boards/revisions covers connectors, electrical paths, and mapping; stacks covers actual API/driver/runtime; integrations covers languages; recipes covers engineering patterns.

An unknown platform, revision, or binding does not block independent investigation and offline development. Defer operations requiring unknown physical mappings, and refresh affected evidence after runtime/API changes.

The complete skill includes this collection, workflows, tools and the read-only probe without sibling skills or a development checkout; keep its output in the user's project. Proposals, evaluation records, device snapshots, user measurements, credentials, SDKs, models, and application artifacts are excluded. See [platform maintenance](common/platform-onboarding.md).

English files are canonical. Adjacent .zh-CN.md translations have the same IDs/applicability and share structured YAML data and original source images; they are not separately matched catalog entries.
