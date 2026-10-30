---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.interfaces-guide
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.v1.0.interfaces
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.schematic-mapping
- board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout
sources:
- source.seeed-schematic-v1
- source.cached-vendor-dts
- source.cached-pinctrl
- source.cached-soc-dtsi
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-20'
---

[English](interfaces.md) | [简体中文](interfaces.zh-CN.md)

# V1.0 接口来源与 Linux 标签差异

官方原理图与vendor源码的映射对照，详见 [J3 完整映射](schematic-mapping.zh-CN.md)。这里保留 vendor DTS 的历史 `gpio-line-names` 声明，用于解释标签为什么不能直接控制物理排针；不将其改写成正确 pinout。

| J3 标签声明 | vendor line-name 指向 pad | 原理图 J3 对应 pad | 一致 |
|---|---|---|---|
| 3 | `GPIO1_C7` | `GPIO4_B4` | 否 |
| 5 | `GPIO1_C6` | `GPIO4_B5` | 否 |
| 7 | `GPIO1_C3` | `GPIO3_C6` | 否 |
| 8 | `GPIO0_D4` | `GPIO0_D4` | 是 |
| 10 | `GPIO0_D5` | `GPIO0_D5` | 是 |
| 11 | `GPIO1_C4` | `GPIO4_A6` | 否 |
| 12 | `GPIO1_D1` | `GPIO4_A0` | 否 |
| 13 | `GPIO2_C0` | `GPIO4_A4` | 否 |
| 15 | `GPIO1_C5` | `GPIO2_B5` | 否 |
| 16 | `GPIO2_B6` | `GPIO4_A1` | 否 |
| 18 | `GPIO2_B7` | `GPIO0_C6` | 否 |
| 19 | `GPIO1_B5` | `GPIO3_D6` | 否 |
| 21 | `GPIO1_B6` | `GPIO3_D5` | 否 |
| 22 | `GPIO2_D7` | `GPIO2_B1` | 否 |
| 23 | `GPIO1_B4` | `GPIO3_D4` | 否 |
| 24 | `GPIO1_B7` | `GPIO3_D7` | 否 |
| 26 | `GPIO1_C0` | `GPIO0_C7` | 否 |
| 27 | `GPIO4_C7` | `GPIO3_B7` | 否 |
| 28 | `GPIO4_C6` | `GPIO3_C0` | 否 |
| 29 | `GPIO3_A2` | `GPIO3_C1` | 否 |
| 31 | `GPIO1_C1` | `GPIO3_C4` | 否 |
| 32 | `GPIO1_D5` | `GPIO0_D3` | 否 |
| 33 | `GPIO1_C2` | `GPIO4_A7` | 否 |
| 35 | `GPIO1_D2` | `GPIO0_C4` | 否 |
| 36 | `GPIO1_D4` | `GPIO4_C7` | 否 |
| 37 | `GPIO3_A3` | `GPIO0_C5` | 否 |
| 38 | `GPIO1_D3` | `GPIO3_A3` | 否 |
| 40 | `GPIO1_D0` | `GPIO3_A2` | 否 |

28个信号标签只有8/10一致。Linux标签关联到的pad并不一定是相同编号的J3物理针脚，必须用原理图与当前控制器身份定位。

[interfaces.yaml](interfaces.yaml) 保存源码标签和逐项比较；[schematic-mapping.yaml](schematic-mapping.yaml) 保存 40 针文档映射、局部 offset、DT 控制器身份、电平转换路径及约束；[official-pinout.yaml](official-pinout.yaml) 保留官方图原标签，包含 26 脚 SPI 标注差异。

板内 GPIO expander、复位/供电、LED、风扇等保持原保护范围。27/28 接共享 I2C4，不能扫描或强制访问；8/10 为调试 UART；不能按官方图把 26 脚作为 SPI3 CS0，也不能把任意风扇PWM节点 当作 32/33 的 PWM。

用户接线时可按[接线图指南与AHT20示例](../../../../../common/wiring-diagrams.zh-CN.md)给出本板的物理针脚定位和逐线连接图。

排针定位图必须按[wiring-layout.yaml](wiring-layout.yaml)记录的主板视角：元件面朝上、排针在上边缘，上排39→1、下排40→2，1/2脚在右端；不能按通用竖向表替代。
