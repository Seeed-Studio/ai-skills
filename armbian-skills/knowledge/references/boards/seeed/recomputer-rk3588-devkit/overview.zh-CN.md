---
schema_version: '1'
id: board.seeed.recomputer-rk3588-devkit.overview
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3588-devkit
required_refs:
- board.seeed.recomputer-rk3588-devkit
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.local-rk3588-board
- source.local-rk3588-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# recomputer-rk3588-devkit 资料入口

vendor compatible为 `seeed studio,recomputer rk3588 devkit`，mainline为 `seeed,recomputer-rk3588-devkit`，分别精确匹配；它们不证明主板revision。实际GPU驱动需从当前系统识别；NPU可能通过DRM节点暴露，不能硬编码renderD编号或以缺/dev/rknpu判定无NPU。

使用 [板级数据](board.yaml) 与 [平台数据](../../../platforms/rockchip/rk3588/platform.yaml)。新增当前 compatible/内核/驱动事实后，按通用流程选择实际 stack；未知 revision 不影响不依赖排针的调查或离线开发。

J10全部40位置、电平路径、复用候选及23/40脚同网限制见[接口指南](revisions/v1.0/interfaces.zh-CN.md)。资料覆盖不等于当前硬件可直接操作。
