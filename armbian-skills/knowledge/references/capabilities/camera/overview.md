---
schema_version: '1'
id: capability.camera
kind: capability
applies_to:
  capabilities:
  - camera
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

[English](overview.md) | [简体中文](overview.zh-CN.md)

# Camera application development

Identify the sensor, CSI/USB interface, media graph, video node, output format, IQ/3A pipeline, and runtime permissions. Do not assume `/dev/video0`. Check sample frames for color, exposure, and content; capturing a frame alone does not establish correct imaging.

Identify each node's actual driver and capture capability: a video node may be HDMI input, an ISP/codec or metadata rather than the requested USB camera. Do not predict the next device number.

If the intended source is not enumerated, the current-stage deliverable is connection/enumeration checks, what output identifies the source, and how to inspect its supported modes. Do not append executable installation, capture or stream configuration based on an assumed source. A capture command's resolution/pixel format/frame rate may come only from the target node's actual enumerated output: issuing a command with a placeholder device (e.g. /dev/videoN) does not make an unverified format choice conditional — what awaits confirmation is the format parameters themselves, not just the device number. A requested roadmap may describe conditional pipeline stages; actual format, frame rate, encoder and receiving/publishing service must be known before producing a runnable recipe. Do not fill those gaps with typical camera specifications, a guessed configuration syntax or package/performance guarantees. Before the actual format, receiving/publishing service and installed software are checked, do not use dependency-floor phrasing ("the minimum is just two packages", "you only need to install X and Y") or closing promises ("... and that's it"): state the software inventory as checked-empty, and "checked-empty" covers only the sources actually checked (e.g. those few commands) — it does not establish that zero-install is impossible, that the target lacks a hardware-encoding build, or that some specific set must be installed; keep the remainder unknown while other sources, containers and private tools are unchecked, and do not write hedged location inferences like "most likely not on this board / probably elsewhere" — the location is simply unknown: write "location unknown, needs confirmation"; list installation as a conditional action after format and receiver checks, never as a default mandatory stage; see [camera verification](verification.md) for staged acceptance and phrasing. Continue independent project implementation if requested, keeping this hardware-dependent configuration unresolved.

For an unlisted platform, continue with official interfaces and bounded tests. If essential wiring or compatibility is unknown, continue offline implementation and mark the dependent hardware steps unverified.
