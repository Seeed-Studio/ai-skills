# Armbian hardware application development

Deliver the user's requested application feature. Existing-project extensions, beginner assistance, and new applications share this workflow; language and runtime form come from the project.

## Understand project and target

Read repository conventions, entry points, dependency/lock files, hardware-access layer, tests, and deployment, preserving user edits. Find original business extension points through [project integration](../references/common/project-integration.md). A standalone hardware demo cannot replace integration. Missing bindings do not justify rebuilding the application or changing language.

Confirm workspace, build environment, runtime device, actual user/container, and deliverable scope. Use existing project/conversation facts before asking again. Explain interface purpose, preparation, and expected observations to beginners without defaulting to Python or services.

Read this package's [index](../references/INDEX.md) and the version summary from `python3 scripts/armbian.py info`. Refresh existing capability evidence when target/kernel/overlay/runtime/application environment changes. Read the next relevant workflow in this package when the task needs it.

## Match and plan integration

Supply current facts/task according to the [matching contract](../references/common/reference-matching.md):

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

Read relevant capability, exact board/revision, platform, actual stack, project-language integration, and recipe. Associate conclusions with reference ID/version and current evidence; old observations do not fill current facts. Unknown platforms can use generic interfaces and official sources. Unlisted does not mean incompatible.

Scale the plan to the task: original business entry points/data flow, resource owner, interfaces/dependencies, known/unknown conditions, errors/cancellation, build/deployment, acceptance/regression, and recovery. The plan is not an added approval process; existing authorization remains valid.

## Implement and deliver

- Complete code, configuration, and business integration in the project using its build/error/configuration conventions. Create only necessary structure for new projects. Do not stop at tool instructions or advice to add an adapter.
- Choose native bindings, Linux APIs, vendor C API/FFI, or existing service APIs according to the project. Check versions, ABI/architecture, and lifetime; do not mandate a common CLI, SDK, or control daemon.
- Define open/close, concurrency, timeout, cancellation, and release. Use an existing owner's interface or modify its implementation rather than bypassing it. Preflight cannot eliminate actual request races.
- GPIO output requires reliable board/revision/connector/electrical/controller mapping plus current mux/consumer. Pause only the uncertain output and continue independent code. Holding follows request lifetime; release guarantees neither level nor original direction. Record known original state and follow [recovery](../references/stacks/linux-gpio-chardev/recovery.md) when needed, without unconditional LOW/input.
- Communication follows device protocol, electrical conditions, and actual bus routing. Do not scan internal I2C or force driver-owned addresses. Distinguish UART TTL/RS232/RS485 and CAN TX/RX from CAN_H/L.
- Integrate NPU/GPU/VPU for the actual model/media/API and driver/runtime. Verify output and actual backend separately; CPU/software fallback is not hardware success.

Read task-relevant [capabilities](../references/INDEX.md) and language integrations as needed. Persistent hardware I/O must not block business event loops; short commands need not become a generic control framework.

Complete relevant stages using [deployment](../references/common/deployment.md) and [verification](../references/common/verification.md): build, project tests, old-function regression, authorized deployment, and physical acceptance. For persistent work, check original business behavior before/during/after it. Follow the language integration for async lifetime and errors. Short commands need no full service workflow.

If the target is unreachable, finish offline implementation/business tests and explicitly mark physical validation unperformed. Give positions/actions/expected readings for manual wiring/measurement without inventing completion.

Deliver actual changes/integration locations, dependencies/build/run instructions, acceptance/regression results, unverified items, and recovery. Across stages retain target, artifact digests, changes, and evidence without credentials.

When the task requires user wiring or measurement, follow [wiring diagrams](../references/common/wiring-diagrams.md): provide task-specific highlighted header pins, peripheral endpoints and a voltage/connection table. Match pin rows/columns, pin1 position and observation side to the actual board using its wiring-layout or reliable board-image evidence; without orientation evidence, show wire endpoints/table only, not a guessed header locator.

Lead with the outcome, deliverables, checks and next action; link lengthy procedures in project documents. Acceptance durations, sample counts and thresholds must come from project requirements or applicable sources. Keep missing values as parameters rather than inventing example defaults.
