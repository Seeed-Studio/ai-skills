---
schema_version: '1'
id: stack.rockchip-rknn.detection
kind: stack_guide
applies_to:
  capabilities:
  - npu
  stack_ids:
  - rockchip-rknn
  soc_ids:
  - rockchip.rk3576
  - rockchip.rk3588
required_refs: []
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-kernel-config
- source.cached-vendor-dts
- source.rknn-project
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-29'
---

[English](detection.md) | [简体中文](detection.zh-CN.md)

# Rockchip RKNPU + compatible RKNN runtime: detection

检查 platform driver、实际设备访问节点、runtime 库和包版本。节点名不能固定为 /dev/rknpu；以实际 driver/runtime 发现为准。

DRM 节点与驱动的对应关系在 `/sys/class/drm/*/device/uevent` 的 `DRIVER=` 字段核对。注意 `device/` 层级：`card*/uevent` 本身只有主次设备号，没有 `DRIVER`，遗漏 `device/` 的路径查询不到任何结果。RKNPU 绑定的可能是 card 或 renderD 节点，按该字段实查，不按编号顺排猜，也不把枚举顺序当应用选择。

包清单和 ldconfig 只覆盖各自管理范围。没有 RKNN 条目时，只能说这些来源未发现；判断应用 runtime 缺失前，检查其配置的库路径、实际加载库和绑定/运行环境。驱动绑定或 debug 计数不证明用户态就绪，空闲计数也不证明从未用过。应用层未知应保留，不由不完整查找直接安排安装。
