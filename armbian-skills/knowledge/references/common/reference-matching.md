---
schema_version: '1'
id: common.reference-matching
kind: common
applies_to: {}
required_refs:
- common.identity
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

[English](reference-matching.md) | [简体中文](reference-matching.zh-CN.md)

# Offline matching contract and reading order

Use `python3 scripts/armbian.py info` for provenance and the index/search for navigation, then choose task-relevant material. catalog.yaml is the maintenance index; catalog.json is generated from the same source for runtime use. The matcher needs only Python standard library. It neither installs application dependencies nor connects to devices or executes commands in references.

Run from the Skill directory:

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

Input contains schema_version="1" and optional target/task/facts objects. Leave missing values null or omitted, without guesses. Arrays must be nonempty and case-exact; versions/architecture names are not normalized. This illustrates structure, not a current target:

```json
{
  "schema_version": "1",
  "target": {
    "device_tree": {"compatible": ["vendor,example-board", "vendor,example-soc"]},
    "board_ids": null,
    "soc_ids": null,
    "hardware_revisions": null,
    "architectures": ["aarch64"],
    "kernel_releases": null,
    "image_ids": null
  },
  "task": {"capabilities": ["gpio"], "operations": ["gpio.output"], "languages": ["rust"]},
  "facts": {"stack_ids": null, "versions": {}, "application": {"device_access": null}}
}
```

Exact current compatible rules may produce board_ids/soc_ids candidates; aliases do not prove identity. Revision requires current evidence, not an old snapshot or the newest directory. Callers remain responsible for input provenance and electrical safety.

applies_to supports board_ids/soc_ids/hardware_revisions/architectures/kernel_releases/image_ids/capabilities/operations/languages/stack_ids. Dimensions combine with AND; allowed values within a dimension use OR. Device dimensions read target, capabilities/operations/languages read task, and stack_ids reads facts. Missing values are unknown, not unsupported.

preconditions, refines.when, and excludes.when use dotted field paths, operator, and value (values for in). Only eq, in, and contains_exact are implemented, comparing strict types/exact values without lexical version ordering. runtime_constraints use component, version_scheme, operator, and expected value from facts.versions. Schemes other than exact produce unknown/review-required. Unknown operators or malformed metadata exit 2; commands are never eval/source inputs.

Results are matches/unknown/no_match/excluded, with per-condition reasons, IDs/paths/digests, and knowledge release. Identity ambiguity appears in identity.conflicts. Missing required references prevent resolution; unmet required material prevents a direct match. related may contain navigation cycles. refines reports conditions/fields for review without automatically overriding protections.

A match establishes reference applicability, not hardware availability or output authorization. Historical reports cannot generate current facts. Read relevant bodies before forming a four-layer capability report and integration plan. --kind narrows display while all metadata/dependencies are still validated.

Optional expected_knowledge_release prevents silent version changes during continuation: a mismatch is a format error requiring review. Use manifest.json to pin knowledge_release and file digests; refresh the task facts explicitly when changing releases. Unlisted platforms can still use common/capability guides and official interfaces without inheriting a similar board's pins.
