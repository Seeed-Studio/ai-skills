---
schema_version: '1'
id: common.project-integration
kind: common
applies_to: {}
required_refs:
- common.identity
- common.linux-device-access
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

[English](project-integration.md) | [简体中文](project-integration.zh-CN.md)

# Extending applications or implementing new features

Read project conventions, entry points, dependency/lock files, existing hardware abstractions, configuration, tests, and deployment. Preserve the language, architecture, and business entry points. Missing bindings do not justify switching language or delivering an isolated demo.

Scale the integration plan to the task: goal/acceptance, original extension points, interface and known/unknown conditions, resource owners/data flow, actual user/container, dependencies/build, disconnect/timeout/cancellation behavior, changes/regression/recovery. A simple plan can remain in the conversation; do not add an approval process.

Choose native libraries, Linux APIs, vendor C API/FFI, or an existing service's public interface according to actual conditions. An existing CLI may fit infrequent management; do not spawn a subprocess for every real-time sample, media frame, or inference. Any binding serves this project rather than imposing a common SDK, control daemon, or JSON protocol.

Integrate into the original business path and preserve user edits. Define open/release and concurrency ownership. Isolate blocking hardware I/O from web/event loops. Expose errors, stale data, busy resources, and timeouts. Create new source/dependency/configuration structure only for a new project.

Before extending, preserve reproducible results and code state for relevant old behavior; rerun it through original entry points afterward. New tests alone do not prove existing behavior survived. Separate a persistent operation's lifetime from its initiating short request. Define business/API cancellation and application shutdown; the original owner retains ownership through cleanup. Degrade according to business semantics and expose the reason when hardware is unavailable, without stopping unrelated business or claiming false hardware success.

For beginners, start with possible features, interfaces, prerequisites, and how to run/observe results. Specify positions/actions/expected observations for wiring or measurements. Distinguish user reports from agent observations; continue independent offline work while waiting for necessary physical actions.

No fixed storage protocol is required for task records. Where useful, retain target, workspace/build environment, capability evidence, artifact paths/digests, code version/uncommitted edits, configuration changes, acceptance, and recovery at the project's established location. Exclude credentials.

When the user must wire hardware, follow [wiring diagrams](wiring-diagrams.md) to provide header locations, wire endpoints and a connection table for the actual board/module.
