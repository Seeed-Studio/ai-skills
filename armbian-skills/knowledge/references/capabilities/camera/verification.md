---
schema_version: '1'
id: capability.camera.verification
kind: capability_guide
applies_to:
  capabilities:
  - camera
required_refs:
- capability.camera
- common.verification
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

# Camera and video pipeline verification

Gather evidence per stage: input enumeration → format/frame rate → encode backend → muxing/transport → receiver decode/display. A successful command or a running pipeline covers only the stages actually exercised; any unverified stage stays unverified and is not covered by other stages passing.

Input identification: a v4l2 enumeration lists that node's capabilities (e.g. MJPG 1920x1080 30fps, YUYV 1920x1080 5fps). It constrains what the node can output, not whether later encode, transport, or the receiver can carry it. Choose capture parameters from enumerated formats, do not predict unlisted modes, and do not treat a high-frame-rate format as a substitute conclusion for a lower-rate one.

Check the encode backend against the target build: libx264 appearing in a command proves only that this command used software encoding. Whether hardware encoding exists follows the target's actual FFmpeg build via `-encoders`/`-hwaccels` output (do not rely on entry names from memory): a missing entry means only "this build did not compile that backend" — never "the board cannot encode in hardware". Different builds or containers on the same board can differ. Acceptance rests on actual encode logs and output stream parameters; before a run, assert neither software nor hardware encoding.

Receiver and deployment location: an RTSP URL proves no receiving/forwarding service is configured or running. Until checked, keep statements about where Home Assistant, go2rtc, or similar components run conditional; "no Docker / no such process on this machine" proves neither that the deployment is elsewhere nor that it is local — and hedge words do not help: never write "most likely not on this board / probably elsewhere"; write "the checked <sources> lack that component; location unknown, needs confirmation". Do not assert dependency floors like "at minimum X and Y must be installed": first check existing publish/receive services, installed software, and application permissions on the target; let the check results decide what is missing. Express installation as a conditional action after format and receiver checks, and do not chain unchecked prerequisites into a closing "... and that's it" promise; "no encode/stream tool among the checked commands" is not "zero-install is impossible" — keep unchecked sources unknown.

Example staged acceptance: capture (frames arrive, format matches) → encode (actual backend, output parameters) → transport (receiver receives the complete stream) → display/record (receiver decodes frames, content checked). Record target, time, commands, and evidence per stage; a downstream user report does not retroactively prove upstream stages.
