---
schema_version: '1'
id: common.linux-device-access
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
updated_at: '2026-11-03'
---

[English](linux-device-access.md) | [简体中文](linux-device-access.zh-CN.md)

# Checking application access

Collect system identity, runtime user, node permissions, service configuration, and container mappings. Use standard Linux interfaces or the project's existing business API. Do not bypass a driver or application's ownership.

Read-only inventory excludes GPIO requests/output, I2C scans, raw-register access, service restarts, overlay changes, GPU benchmarks, and model inference. Define inputs, duration, stopping conditions, and acceptance separately for functional tests.

The supplied `probe_device.py` needs no credentials file. Authenticate SSH in the operator's terminal and save output on the host. This probe inspects the environment; it is not functional hardware evidence.

Node existence, owner/mode/ACL listings, `id`, and `test -r`/`test -w` are permission predictions, not evidence that the application opened or used the device. A successful metadata check only permits the next authorized check; do not label it "application access verified" or close an access fact from it. A real open, an operation through the actual API, and the requested business result are further distinct observations. Verify in the actual user/service/container context: a shell under the same UID can still differ in device cgroup, namespace, capabilities, ACL/LSM or service restrictions. Do not add device I/O to a metadata-only request just to obtain stronger evidence.
