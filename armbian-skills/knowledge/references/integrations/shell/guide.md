---
schema_version: '1'
id: integration.shell.guide
kind: integration
applies_to:
  languages:
  - shell
required_refs:
- common.project-integration
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

[English](guide.md) | [简体中文](guide.zh-CN.md)

# Shell project integration

A one-shot command is a valid application deliverable. Check the installed tool's help/version; do not mix libgpiod 1.x/2.x syntax or holding behavior. Specify target, arguments, duration, exit codes, process ownership/release, and state after disconnection. Treat inputs as arguments. Short commands do not require a resident service, and high-frequency workloads need not use a shell wrapper.
