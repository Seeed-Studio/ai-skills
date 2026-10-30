---
schema_version: '1'
id: common.wiring-diagrams
kind: common
applies_to: {}
required_refs:
- common.identity
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.schematic-mapping
- board.seeed.recomputer-rk3588-devkit.v1.0.interfaces
- board.seeed.recomputer-rk3576-devkit.v1.0.wiring-layout
- board.seeed.recomputer-rk3588-devkit.v1.0.wiring-layout
sources:
- source.seeed-schematic-v1
- source.seeed-rk3588-v1-schematic
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-22'
---

[English](wiring-diagrams.md) | [简体中文](wiring-diagrams.zh-CN.md)

# 向用户展示本次任务如何接线

任务需要用户连接外设或测量仪表时，在请用户动手前，给出针对本次任务的接线示意图和简短接线表，使用用户的语言。纯能力查询只在有助于理解时配图，不因此自动执行硬件操作。

## 图里应包含什么

- 写明精确板型/revision和连接器。RK3576 DevKit V1.0 使用 **J3**，RK3588 DevKit V1.0 使用 **J10**；同属一个SoC家族或排针外形类似树莓派，不代表可以套用接线。
- 两端都标出物理脚号与信号名称，以及供电、信号电压。不用 Linux `PIN_*` 标签、gpiochip编号或GPIO offset代替连接器位置。
- 将“与主板实际排布一致、高亮所需针脚的排针定位图”与“每根线连接两端的图”配合使用。端点明确、文字清楚，可用颜色辅助，但不能只靠颜色识别；灰色未用针脚不表示也要接线。
- **排布必须与主板一致。** 使用对应板型/revision的 `wiring-layout.yaml` 或有依据的PCB布局/实物照片，明确元件面或焊接面、连接器所在板边、1脚所在端、奇偶行和编号递增方向。图中行列、左右上下和标志物必须在同一视角下与主板一致；不能按通用奇偶表任意竖排、镜像或旋转来充当定位图。需要旋转时必须连同整个板视图和标志物一起变换。缺少实物方向依据时，只给逐线连接图与接线表，询问方向或索取清晰照片，不猜排针定位；继续独立代码工作。
- 以外设丝印/数据手册识别端子，不根据传感器名称猜模块针脚排列。没有精确物理布局时，用带端子名的方框表示模块。
- 说明与任务有关的总线共享、复用、共地和电压兼容要求。I2C为SDA接SDA、SCL接SCL；UART为TX接RX、RX接TX且电平匹配；SPI按已核对的CS路径连接；CAN/RS485按实际收发器接口，不能拿原始GPIO猜接线。

需要图片时，根据已核对映射直接绘制SVG等确定性矢量图，AI生成的板卡外观图不能作为连线依据。无法显示图片时用Mermaid或纯文本；始终保留接线表，避免图形渲染失败后丢失操作信息。本次任务的图保存到用户项目，不把当前接线确认或实测电压写进静态references。

先使用已有会话事实，再询问影响任务的模块、电压或方向等缺失条件。更改接线通常应先断电，确认实际接好后继续已有授权范围内的操作。示意图不证明用户已接好，也不证明总线/驱动就绪；GPIO输出仍需核对当前mux/owner。

## AHT20示例：先选正确板卡

示例适用于 **VCC与I2C信号均兼容3.3V** 的模块，需要核对用户实际模块。两张排针图都采用**元件面朝上、40-pin位于主板上边缘**的参考视角；上排从左到右39→1，下排40→2，1/2脚在右端，与各板已记录的主板方向一致。用户需将实物按同一视角对齐，不能直接对照焊接面或镜像照片。外设方框表示端子标签，不表示模块的实际针脚顺序。

| AHT20端子 | RK3576 DevKit V1.0 | RK3588 DevKit V1.0 |
|---|---|---|
| VCC | J3-1，3.3V | J10-1，3.3V |
| GND | J3-14，GND | J10-14，GND |
| SDA | J3-27，I2C4 SDA | J10-27，I2C6 SDA |
| SCL | J3-28，I2C4 SCL | J10-28，I2C6 SCL |

### RK3576：J3 / I2C4

![RK3576 J3 AHT20接线示例](../boards/seeed/recomputer-rk3576-devkit/revisions/v1.0/assets/aht20-wiring.svg)

排布依据[官方主板实物图](../boards/seeed/recomputer-rk3576-devkit/revisions/v1.0/official-pinout.zh-CN.md)，方向数据见[wiring-layout.yaml](../boards/seeed/recomputer-rk3576-devkit/revisions/v1.0/wiring-layout.yaml)。电气连接依据[RK3576原理图映射](../boards/seeed/recomputer-rk3576-devkit/revisions/v1.0/schematic-mapping.zh-CN.md)。J3-27/28虽然官方标注为EEPROM相关信号，实际位于有板载client的共享I2C4总线，并非传感器专用总线；不绕过内核地址占用，也不盲扫总线来选接线。

### RK3588：J10 / I2C6

![RK3588 J10 AHT20接线示例](../boards/seeed/recomputer-rk3588-devkit/revisions/v1.0/assets/aht20-wiring.svg)

排布依据维护者确认的元件面视角，方向数据及来源见[wiring-layout.yaml](../boards/seeed/recomputer-rk3588-devkit/revisions/v1.0/wiring-layout.yaml)；不是从RK3576推导。电气连接依据[RK3588接口映射](../boards/seeed/recomputer-rk3588-devkit/revisions/v1.0/interfaces.zh-CN.md)。J10-27/28为共享I2C6，包含Type-C和RTC等client；解析实际adapter与地址可用性，不直接假定 `/dev/i2c-6`。

仅支持文本的RK3588回答可使用：

```text
RK3588 DevKit V1.0 / J10       AHT20模块（按端子丝印）
J10-1   3.3V  --------------- VCC
J10-14  GND   --------------- GND
J10-27  SDA   --------------- SDA
J10-28  SCL   --------------- SCL
```

GPIO/万用表任务还需画明表笔极性，例如RK3576红笔接J3-15、黑笔接J3-6；RK3588红笔接J10-15、黑笔接J10-6。电压档跨接信号和地，不能画成电流表串接。两块板的15脚对应不同SoC pad和Linux offset，不能只替换连接器名称就复用应用GPIO配置。

其他外设、平台沿用这种表达方法，但必须使用各自已核对的连接器映射、电压和协议。这里的AHT20接线不是所有I2C项目的默认接法。

## 新增板卡或视角

每个板型/revision单独维护 `wiring-layout.yaml`，记录方向来源、观察面、连接器板边、1脚端及按该视角排列的物理脚号矩阵。原理图网络表只能说明电气连接，不能替代PCB实物方向依据；来源未知时禁止生成排针定位图。示例生成器遇到不支持的视角会报错，维护者需按对应布局调整坐标后再发布，不能静默套用已有板卡。
