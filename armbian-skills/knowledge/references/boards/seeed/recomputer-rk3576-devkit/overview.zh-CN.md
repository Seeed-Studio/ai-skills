---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.overview
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
- source.seeed-product
- source.local-board-config
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](overview.md) | [简体中文](overview.zh-CN.md)

# RK3576-20/30 应用开发入口

适用于reComputer RK3576-20/30整机DevKit的参考设计，对应Armbian `recomputer-rk3576-devkit`。Module Dev Kit使用另一载板，不能互用排针表；实际产品、PCB revision和方向需逐台确认。

- [板卡数据](board.yaml)：产品接口、精确compatible候选、EEPROM路由码与DTB差异。
- [40-pin官方标注](revisions/v1.0/official-pinout.zh-CN.md)：全部40个位置及官方方向、电源/GND声明。
- [原理图到SoC映射](revisions/v1.0/schematic-mapping.zh-CN.md)：net、pad、局部offset、电平转换及26个错误Linux标签差异。
- [接口来源与冲突](revisions/v1.0/interfaces.zh-CN.md)：vendor标签声明不能作为正确pinout。
- [Overlay源码清单](overlay-inventory.yaml)与[镜像配置](revisions/v1.0/configuration.zh-CN.md)：候选功能与冲突；目标是否安装或启用需另查。
- [外设](../../../platforms/rockchip/rk3576/peripherals.zh-CN.md)与[加速器](../../../platforms/rockchip/rk3576/accelerators.zh-CN.md)：GPIO/I2C/UART/SPI/CAN/PWM、NPU、GPU与VPU接入条件。
- [任务前需确认的信息](questions.zh-CN.md)。

已有应用先分析语言、构建和业务入口，再选择实际软件栈；节点存在、单项成功或文档标注不能替代当前应用的功能验证。
