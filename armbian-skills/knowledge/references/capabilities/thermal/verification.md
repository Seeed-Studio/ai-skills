---
schema_version: '1'
id: capability.thermal.verification
kind: capability_guide
applies_to:
  capabilities:
  - thermal
required_refs:
- common.verification
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-30'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# Thermal and fan verification

Layer a thermal question first: zone attribution and trips, CPU policy/governor/limits, workload, and time. When quoting any number, label its source (static snapshot or sampling series) and moment; a static snapshot's range is not the series' full range, and "all temperatures" is wrong when the series contains lower/higher values.

Conclusion phrasing, side by side:

- Never write "the fan is installed and spinning slowly" or "the stock fan is speeding up". An enabled PWM channel, a duty value, or a duty that rises with temperature proves only control output: write "the fan channel is claimed by pwm-fan at duty X%; whether a fan is physically installed and turning is unverified". A parenthetical "speed/airflow unverified" does not undo the physical claim in the main sentence. Physical evidence is observed rotation, a tach/RPM reading, or a reproducible temperature/airflow change.
- Never write "completely idle / zero load". A rounded loadavg of 0.00 is only "loadavg sampled 0.00 (rounded)"; it is not per-core instantaneous state.
- Keep frequency attribution conditional: write "consistent with this governor's idle behavior; ruling out thermal limiting requires same-instant observations", where same-instant means one loop reading current frequency together with `scaling_max_freq`/`cooling_device*/cur_state` — never splicing snapshot values with series values.

Workload and sampling phrasing: a diagnostic load never mandates a fixed duration ("must run ten minutes at full load"); the criterion outranks duration — stop once "temperature vs. trip" and "max clamped or not" are answered. Without a project basis, offer a short bounded load and note it is adjustable. Fallback load commands carry their own time limit (e.g. `timeout 300 stress-ng --cpu 8` or `timeout 60 yes >/dev/null`), never unbounded loops; samplers state their count or total duration (e.g. a `for i in $(seq N)` loop of fixed rounds), never a resident `watch` with no stopping method. Keep fan/throttling recommendations conditional until load and physical evidence exist.
