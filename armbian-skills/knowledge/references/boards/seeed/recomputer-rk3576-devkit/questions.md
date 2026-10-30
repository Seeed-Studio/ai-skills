---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.questions
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
required_refs:
- board.seeed.recomputer-rk3576-devkit
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout
sources:
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](questions.md) | [简体中文](questions.zh-CN.md)

# Information to confirm for the current task

1. Is the product an RK3576-20/30 full-system DevKit or Module Dev Kit? Does PCB silkscreen match the reference revision?
2. What are current compatible, kernel, DT, driver/runtime, and actual application user? Leave unevidenced fields unknown.
3. Which connector/physical pins are used? Confirm peripheral model, protocol/address, supply, signal levels, load, and actual wiring.
4. What are the project language, business entry points, build, and deliverable form? Which existing behavior must remain?
5. How can physical effect, error handling, and release be checked with minimal manual actions? Automate independent checks first.

Use [official labels](revisions/v1.0/official-pinout.md) and [schematic mapping](revisions/v1.0/schematic-mapping.md). Do not request known information again; ask only for gaps affecting the operation.
