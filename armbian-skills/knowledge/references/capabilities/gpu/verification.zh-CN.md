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

# GPU 验证

按实际图形或计算 API 分别测试，记录 renderer/device/provider、上下文创建路径和输出。软件 renderer 或 CPU fallback 不计硬件通过；渲染成功不推导 OpenCL/Vulkan 计算可用。桌面用户通过不等于 headless 服务通过。

Vulkan 设备枚举与应用实际选择的物理设备分别判断，排在首位不保证被选中。软件设备可以与 EGL 上下文实际使用的硬件 renderer 并存；要判断应用，需在其实际用户/会话/容器中看自己的 renderer/选卡证据。

从已绑定 GPU 枚举实际 sysfs 路径，不猜设备目录名。活动计数只作旁证：短任务可能漏采，其他进程也可贡献活动。单次 GPU 负载为零、CPU 占用高不能直接证明软件回退。
