---
name: armbian-hardware
description: Explain Armbian device capabilities, integrate hardware into existing applications, deploy and diagnose their behavior. Use for board peripherals, sensors, cameras and NPU/GPU/VPU application work on Armbian; ordinary Linux tasks need no hardware workflow.
---

# Armbian hardware applications

Deliver the requested feature or explanation using the project's language, business entry points and native tooling. Reuse known project/target facts and existing authorization. Distinguish workspace, build host and runtime device; an unreachable target does not prevent independent offline work.

## Choose only the relevant workflow

| Request | Read |
|---|---|
| What can this device do, through which interface, and what is missing? | [Capabilities](workflows/capabilities.md) |
| Extend an existing app or implement a hardware feature | [Integration](workflows/integrate.md) |
| Install/update an artifact, CLI, service or container | [Deployment](workflows/deploy.md) |
| Explain a failure or prove business/hardware behavior | [Verification](workflows/verify.md) |

Start at the requested stage; read another workflow only when needed to complete the task. Do not load every workflow or the complete knowledge index. A short question needs no full project plan or deployment process.

For diagnosis, answer the present question and give the smallest useful next check within the user's scope. Keep observations, inferred causes and unverified effects separate. A limited search without results does not prove absence; registered/enabled hardware does not prove physical operation or use by the application. Follow [evidence interpretation](references/common/verification.md) before turning observations into installation, wiring or workload advice.

## Find applicable knowledge

Run commands relative to this skill's directory, from the operator's host. Python 3.9+ standard library is sufficient. These commands are offline and never control hardware:

```bash
python3 scripts/armbian.py info
python3 scripts/armbian.py search "container video hardware decode" --facts /project/task-facts.json
python3 scripts/armbian.py match --facts /project/task-facts.json
python3 scripts/armbian.py explain --ref common.identity --facts /project/task-facts.json
```

Use `info` for version and provenance; do not print the full manifest hash map. Search accepts Chinese/English symptoms and returns candidates. Reuse existing task facts with `--facts` to filter known mismatches; do not invent facts to narrow results. Without facts, applicability is unknown. Ranking never proves identity, compatibility, pin mapping or availability. Use the returned absolute `read_path` to open a reference; `path` is relative to `reference_root`, not the skill root. Read the selected reference and the complete required dependency closure reported by explain. Follow the [matching contract](references/common/reference-matching.md); missing revision/version/access stays unknown, never borrow another carrier's pins.

For physical connector positions, query the documented table instead of reading the whole YAML:

```bash
python3 scripts/armbian.py pins --board seeed.recomputer-rk3588-devkit --revision v1.0 --connector J10 --pins 23 40
```

Use exact selectors justified by the task; they select documentation, not a verified target. Add `--facts` when current facts exist. Output includes complete selected pin records, shared-net partners, electrical/operation constraints, sources and required reference IDs. Use `explain` for dependencies; read full material only for missing context or conflicts. Unknown board/revision/connector must not fall back to a similar profile. Nominal voltage alone does not justify direct LED/load drive or a resistor value when drive-current limits and component specifications are unknown.

If Python is absent, use the relevant workflow and [reference navigation](references/INDEX.md) directly; do not install dependencies merely to run discovery. For current target metadata, optionally transmit `scripts/probe_device.py` over the user's authorized SSH connection as described in the capabilities workflow. The probe performs bounded read-only discovery, not bus scans, GPIO requests or workloads.

## Continue across stages

For sustained work, reuse existing project records or optionally copy [task facts](templates/task-facts.json) and [plan](templates/plan.md) into a project-local `.armbian/` directory. Simple questions need no files. Record evidence source, target and time; keep credentials out. Refresh affected observations after target, image/kernel, routing, user/container, application or input changes. A stored plan does not override electrical constraints.

Report hardware/interfaces, system readiness, actual application access and functional results separately. Distinguish static references, user reports, software observations, offline tests and physical measurements. A node, successful command or correct output alone does not prove hardware acceleration or electrical behavior. Use [wiring guidance](references/common/wiring-diagrams.md) when the user must wire or measure hardware.

Finish the authorized work and relevant regression. State implemented/deployed/verified scope, remaining unknowns and concrete recovery steps without inventing device access or physical acceptance. Summarize the outcome, changes, verification and next action first. Put substantial deployment/recovery detail in linked project deliverables, without duplicating it in the main answer. Derive acceptance durations, sample counts and thresholds from the project SLA, sampling period or authoritative requirements; leave unresolved values explicit. Use `info` for package provenance; the full manifest remains available for integrity auditing.
