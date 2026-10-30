---
schema_version: '1'
id: capability.gpu.verification
kind: capability_guide
applies_to:
  capabilities:
  - gpu
required_refs:
- capability.gpu
- common.verification
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.vulkan-device-selection
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](verification.md) | [简体中文](verification.zh-CN.md)

# GPU verification

Test each graphics or compute API separately. Record renderer/device/provider, context creation, and output. Software rendering and CPU fallback do not count as hardware passes. Successful rendering does not establish OpenCL/Vulkan compute support; a desktop-user result does not establish headless-service access.

Separate Vulkan device enumeration from the physical device chosen by the application; being first does not guarantee selection. A software device can coexist with a hardware renderer used by an EGL context. Check the application's own renderer/selected-device evidence in its actual user/session/container before making an application claim.

Discover the bound GPU's actual sysfs paths instead of guessing a device basename. Activity counters are supporting evidence: short work can be missed and other processes can contribute activity. Zero sampled GPU load plus high CPU usage alone does not establish software fallback.
