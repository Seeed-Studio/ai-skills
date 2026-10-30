---
schema_version: '1'
id: common.deployment
kind: common
applies_to: {}
required_refs:
- common.linux-device-access
- common.capability-evidence
preconditions: []
refines: []
excludes: []
related: []
sources: []
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](deployment.md) | [简体中文](deployment.zh-CN.md)

# Deployment, runtime identity, and recovery

Follow the application's existing deployment model. Identify workspace, build environment, target, and installation directory. A one-shot command need not become a service. Check source version/digest, architecture, dynamic linker, and library ABI before transferring artifacts to target staging. A host build does not prove target execution.

Preserve affected versions/configuration and executable recovery steps before changes. Replace only project-owned files and retain existing configuration and user edits. Prepare and check the deployment first, then proceed within existing authorization. Scope permissions to the necessary device/user; do not make every node writable or grant unrestricted passwordless root.

Use the target's actual service manager: runtime user, WorkingDirectory, environment/dependencies, readiness, logging, stop timeout, resource release, and restart policy. Check how hardening affects device/library access; do not blindly apply PrivateDevices when it hides required devices. Explain repeated hardware output after crash/restart.

Check the process, manager running state, business readiness, and hardware function separately. Running alone is incomplete. Verify startup behavior when boot-time operation is requested; reboot only when necessary and authorized. Do not stop a shared service to cancel one task.

After SSH loss or timeout, inspect the original process/logs/artifacts and device state before retrying. Report uncertainty if the outcome cannot be retrieved; adding a request ID does not guarantee deduplication. Preserve cancellation/recovery results. Restoring configuration is not proof that external hardware recovered.
