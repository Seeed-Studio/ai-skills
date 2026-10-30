# Armbian device capabilities

Help users understand what the device can do, through which interface, what is missing, and how to integrate it into an application. For a capability-only request, deliver an evidence-based explanation and next steps.

## References and target

Start with this package's [index](../references/INDEX.md), [identity rules](../references/common/identity.md), and actual version from `python3 scripts/armbian.py info`. Historical reports are not current target state.

Distinguish workspace, build host, and runtime device. Use the user's specified authorized local/SSH/terminal connection without requiring a particular MCP. A failed connection does not justify running target hardware operations on the host. Use current compatible, system/kernel, and hardware identity for board/SoC candidates. Unknown revision stays unknown; a matching SoC does not establish another carrier's pinout/electrical conditions.

## Collection and matching

When Python 3 is available, run scripts/probe_device.py on the confirmed target. Remotely, the operator can use `ssh TARGET 'python3 -' < scripts/probe_device.py`. Authenticate through normal SSH or the connector, without credentials in commands/files. Without Python, use available read-only interfaces as needed rather than installing dependencies by default.

The probe performs bounded metadata collection only: no GPIO requests, I2C scans, device transactions, service/overlay changes, or accelerator workloads. Missing tools, denied access, truncation, and timeout remain unknown rather than proving unsupported hardware. EEPROM identification is explicitly optional and requires confirmed applicability.

Following the [matching contract](../references/common/reference-matching.md), pass current facts/task as JSON with missing fields null; use `--facts -` for stdin when no persistent project record is needed:

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

The matcher filters local references on the operator's host using Python standard library, without connecting to the target. Read task-relevant board/revision, capability, platform, and actual stack. matches is not a hardware-availability claim; do not resolve conflicts/ambiguity by taking the first result.

## Explain capabilities

Use the [four evidence layers](../references/common/capability-evidence.md): hardware/interfaces, system readiness, actual application access, and functional results. Label each operation available/needs-setup/busy/unsupported/unknown with source, collection time, target/version, and untested scope.

- Headers: separate physical connector position, protocol/electrical conditions, SoC pad, and Linux controller/line. Preserve official/runtime PIN-label conflicts instead of outputting by label. A controller label is not a fixed device path; resolve it through [GPIO detection](../references/stacks/linux-gpio-chardev/detection.md).
- Acceleration: assess NPU, GPU graphics/compute, and VPU decode/encode separately. Nodes, libraries, feature lists, and nominal performance do not prove actual execution.
- Applications: root-shell enumeration does not establish service/container access. Relate capabilities to the existing project's collector, business API, or media pipeline.
- Unknown platforms/combinations: continue investigating generic official interfaces. Missing header mapping need not block independent acceleration work or offline coding.

Explain possible features, interfaces, prerequisites, and next steps before expanding API/node details. Ask only for missing facts affecting the task. Do not default to side-effectful tests or service deployment.

When the task requires user wiring or measurement, follow [wiring diagrams](../references/common/wiring-diagrams.md): provide task-specific highlighted header pins, peripheral endpoints and a voltage/connection table. Match pin rows/columns, pin1 position and observation side to the actual board using its wiring-layout or reliable board-image evidence; without orientation evidence, show wire endpoints/table only, not a guessed header locator.

For physical connector positions, prefer `scripts/armbian.py pins` with exact board/revision/connector selectors and the requested positions. Keep shared-net and electrical constraints; avoid dumping the entire pin table.

Lead with the outcome, deliverables, checks and next action; link lengthy procedures in project documents. Acceptance durations, sample counts and thresholds must come from project requirements or applicable sources. Keep missing values as parameters rather than inventing example defaults.

For load or LED wiring, nominal GPIO voltage is not drive-current evidence. If maximum current or component ratings are missing, leave direct-drive feasibility and resistor values unresolved. Offer signal endpoints for a suitably specified external driver, or request the missing component/current evidence; do not invent a usual resistor value.
