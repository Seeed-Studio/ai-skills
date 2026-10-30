---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.questions
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
required_refs:
- board.seeed.recomputer-rk3576-devkit
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout
sources:
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](questions.md) | [简体中文](questions.zh-CN.md)

# 当前任务需要确认的信息

1. 产品是RK3576-20/30整机DevKit还是Module Dev Kit？PCB丝印是否与参考revision一致？
2. 当前compatible、内核、DT、驱动/runtime与实际应用用户是什么？没有证据的字段保持未知。
3. 使用哪个连接器和物理针脚？外设型号、协议地址、供电、信号电平、负载及实际接线是什么？
4. 项目语言、业务入口、构建与交付方式是什么？哪些现有行为需要保留？
5. 如何用最少的人工步骤确认物理效果、异常处理与释放状态？能用自动检查的部分先自动完成。

参考[官方标注](revisions/v1.0/official-pinout.zh-CN.md)和[原理图映射](revisions/v1.0/schematic-mapping.zh-CN.md)。无需重复索取已知资料，只补足影响本次操作的缺口。
