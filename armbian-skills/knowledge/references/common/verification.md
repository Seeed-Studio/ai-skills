---
schema_version: '1'
id: common.verification
kind: common
applies_to: {}
required_refs:
- common.capability-evidence
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

# Task acceptance and evidence

Choose necessary source/build, business, target-access, physical-effect, actual-backend, lifecycle, and service-readiness checks from the user's goal. Regress affected old behavior when extending a project. A standalone hardware demo or simulation does not replace application integration.

Define inputs, duration, resources, stopping method, and pass criteria first. Record actual commands/method, target/time, user/container, artifact/dependencies, output, and evidence source. Separate not-tested, passed, failed, and uncertain results. Use `available/needs-setup/busy/unsupported/unknown` for each operation's four capability layers; process exit alone is not a physical pass.

## Interpret observations within their scope

| Observation | What it establishes | What still needs evidence |
| --- | --- | --- |
| No entry in a package list, loader cache or sampled log | Not found in that checked source/context | Application-private libraries, another environment, or unsampled history |
| Driver bound, channel requested/enabled | Software configuration and ownership | A fan rotating, a servo moving, a waveform or a peripheral responding |
| Device enumerated or listed first | A candidate available to that API/context | The device selected by a particular application |
| Utilization or frequency sample | That counter's value during its sampling window | A cause or attribution to a particular process |

Report the strongest supported conclusion, then the missing discriminator. Keep a plausible explanation conditional; do not turn it into a proven cause. Uncollected logs are unknown, not empty. Conflicting snapshots call for synchronized observations, not a guessed daemon or policy change.

For temperature/frequency questions, correlate zone `type`, configured trips, CPU policy/governor/limits, workload and time. Check zone attribution against `thermal_zone*/type` first: trips of zones on one SoC can differ by tens of degrees, and a number like `zone0` says nothing about attribution — do not compare against thresholds before attribution is confirmed. A single temperature reading plus a single frequency reading (even if they appear consistent) does not attribute thermal throttling: it needs simultaneous policy limits, governor, trip state, and a time series. Limits from a static snapshot are not contemporaneous with current frequencies from a sampling series; never splice them into a same-instant argument. Verify per policy (clusters have different limits; quote the numbers per policy). Phrase causal conclusions as "consistent/inconsistent with thermal limits; observation X still needed to discriminate", never "definitely thermal throttling". Rounded load averages are not instantaneous per-core utilization; low frequency alone does not establish thermal throttling. A temperature question need not start a stress test. If a workload test is relevant, use the actual business load or a justified bounded substitute, with a stopping method for both load and sampling — a fallback load command must carry its own time limit or stop method (e.g. `timeout`); do not supply unbounded commands. Keep load/throttling advice conditional and do not turn sample durations or workloads into universal requirements. Do not invent a universal duration.

For fans, PWM duty (including a change with temperature) establishes the commanded output, not installation, rotation or acceleration. Use tachometer/RPM data, an instrument or a specific physical observation for motion; without it report only the control change. Keep this distinction in follow-up checks and the closing conclusion as well as the initial diagnosis.

Check GPIO ownership, normal exit/cancellation, busy resources, disconnection, and relevant failures. Software readback alone does not establish voltage; use an instrument, confirmed wiring, loopback, or specific user observation. Never invent physical actions or readings. Treat request release, direction/configuration restoration, and external-device state separately. Record known original state before restoration and follow [GPIO recovery](../stacks/linux-gpio-chardev/recovery.md); do not guess unknown settings.

For NPU/GPU/VPU, verify output correctness and actual execution backend. Identify CPU/software fallback, and assess video encode/decode and pipeline stages separately. Benchmarks, nominal performance, and CPU utilization cannot replace backend evidence.

When the device is unreachable, continue coding and offline business checks and mark physical validation unperformed. Recheck only affected evidence after environment/input changes. A new combination can receive a bounded test once conditions are known; keep results in the project first. Changes to shared support claims require separate review.

Deliver concise results: implementation/integration locations, build/run instructions, versions/changes, acceptance/regression results, unverified items/next steps, and deployment/recovery. Do not mechanically add an unrelated testing framework.
