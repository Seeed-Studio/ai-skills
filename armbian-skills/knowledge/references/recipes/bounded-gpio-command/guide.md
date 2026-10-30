---
schema_version: '1'
id: recipe.bounded-gpio-command.guide
kind: recipe_guide
applies_to:
  capabilities:
  - gpio
  operations:
  - gpio.output
required_refs:
- recipe.bounded-gpio-command
preconditions: []
refines: []
excludes: []
related:
- stack.linux-gpio-chardev.recovery
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](guide.md) | [简体中文](guide.zh-CN.md)

# A bounded GPIO feature for beginners

Explain the connector, logic levels, external load, and current-limiting/measurement preparation. Confirm reliable pin-to-net mapping, electrical conditions, mux, and current ownership before choosing the project's command/program. Hold the request until expiry/cancellation and record exit/release behavior. Check physical effect and busy/cancel/failure paths. Do not create a daemon/service by default. Without a reliable mapping, complete code/logic tests first without driving output.
