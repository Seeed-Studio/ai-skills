# Armbian application deployment

Deliver the correct artifact to the correct device using the project's deployment model, verifying business readiness and required hardware access.

## Recover context

Read existing integration plans, deployment conventions, source/user edits, artifact digests, and build conditions. Identify workspace, build host, runtime target, deployment directory, actual user/container, and existing authorization.

Start with this package's [index](../references/INDEX.md), `python3 scripts/armbian.py info`, and [deployment guide](../references/common/deployment.md). Select actual dependencies using the [matching contract](../references/common/reference-matching.md):

```bash
python3 scripts/armbian.py match --facts /path/to/task-facts.json
```

Read matching stack/language references and board restrictions without depending on another Skill or development checkout. Historical nodes/versions are traceability only; confirm current target/invalidation conditions rather than inferring compatibility from branch names.

## Prepare and execute

- Verify artifact provenance, target architecture, dynamic linker/ABI, libraries, and configuration. A host build is not target execution evidence.
- Preserve affected original versions/configuration and prepare staging, validation, switching, and executable recovery. A test-directory run is not a system installation. Finish preparation and proceed within existing authorization.
- Follow project directories, packages, containers, or actual service managers. Modify only project scope and preserve user configuration. Limit permissions to required devices/users, without globally writable nodes or unrestricted passwordless root.
- Service configuration includes user, working directory, environment/dependencies, logs, readiness, stop timeout, and suitable restart policy. Check isolation that hides devices/libraries and repeated output after crashes. Create systemd configuration only when the task needs it.
- Install overlays/drivers/runtimes or restart services only when necessary, compatible, impact/recovery understood, and authorized. Canceling a task does not stop a shared service. Assess whole-device reboot separately for necessity and authorization.
- After SSH loss/timeout, inspect the original operation before retrying. Do not blindly replay hardware transactions. A request ID does not guarantee deduplication; report uncertainty when state cannot be confirmed.

For an existing hardware service without a documented live-update contract, confirm the service and its workers have stopped and released resources before changing `current` or effective unit configuration. Follow the project's proven hot-update mechanism when one exists. Capture the previous release and affected unit/drop-ins, then switch, reload changed unit configuration, start, and check real business readiness; rollback must cover both program and changed unit state while preserving calibration. Do not infer that a repeated device error after rollback rules out application or configuration faults.

## Verify and deliver

Check actual service/worker UID, groups and device visibility (including its namespace and device policy), rather than substituting host `id` or `sudo -u`. Check dependencies/permissions as the actual user/container using [device access](../references/common/linux-device-access.md). Follow [acceptance](../references/common/verification.md) to distinguish process, manager running, business ready, and hardware function. If the business entry point or acceptance criteria are missing, give the required evidence and leave functional acceptance pending; active state and quiet logs are insufficient. Verify boot behavior when requested, without rebooting for unrelated checks.

Diagnose/recover at the failure's scope; external hardware recovery requires separate evidence. Deliver artifact version/digest, file/configuration changes, execution location, readiness/hardware results, and recovery steps. If only preparation is complete or the target is unreachable, state not-deployed/not-physically-verified rather than claiming deployment success.

Lead with the outcome, deliverables, checks and next action; link lengthy procedures in project documents. Acceptance durations, sample counts and thresholds must come from project requirements or applicable sources. Keep missing values as parameters rather than inventing example defaults.
