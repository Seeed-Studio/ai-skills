---
schema_version: '1'
id: board.seeed.recomputer-rk3588-devkit.v1.0.interfaces-guide
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3588-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3588-devkit.v1.0.interfaces
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.seeed-rk3588-v1-schematic
- source.local-rk3588-soc-dtsi
- source.local-rk3588-pinctrl
- source.local-rk3588-vccio3-pinctrl
- source.local-rk3588-vendor-dts
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-21'
---

[English](interfaces.md) | [简体中文](interfaces.zh-CN.md)

# RK3588 V1.0 J10：全部40个位置

本表按官方 V1.0 原理图覆盖全部40个物理位置。这里完成的是资料核对，不是40针实机功能测试；每次任务仍需确认实际 PCB revision、连接器方向、装配和软件配置。不能套用 RK3576 的 J3 表。

**J10-23与J10-40同网：** 官方 V1.0 原理图第28页将两者均连接至 `GPIO2_C0_3V3`，对应 `GPIO2_C0`、gpio2局部offset16，也可复用为 SPI1 CLK M0。它们不是两个独立 GPIO，不能分别设置相反电平。40个位置中有28个信号位置、27个不同 GPIO pad。

原理图中28个信号位置均连接具备 GPIO 功能的 SoC pad，但不代表当前可直接作为 GPIO：I2C 总线共享、UART2 为调试路径、SPI1 还有扩展接口走线，必须检查当前复用与驱动占用。4个电源位置和8个 GND 不是 GPIO。结构化数据见 [interfaces.yaml](interfaces.yaml)。

## 全部物理引脚

`gpioN / offset` 表示 DT 控制器标签与**bank 内局部偏移**，不是 `/dev/gpiochipN`。电平路径方向为 SoC 到排针，A/B 是转换器通道。信号排针侧均为标称3.3V。所列复用功能是经源码核对的候选，需要匹配 pinctrl 和驱动配置，并非全部复用矩阵。

| J10物理脚 | 原理图排针网络 | SoC pad；gpioN / 局部offset | 电平路径 | 部分功能 / 限制 |
|---|---|---|---|---|
| 1 | `EXT_3V3` | — | 3.3V 电源 | 电源，不是GPIO |
| 2 | `VCC_5V0` | — | 5V 电源 | 电源，不是GPIO |
| 3 | `I2C3_SDA_M1` | `GPIO3_C0`; gpio3 / 16 | 3.3V直连 | I2C3 SDA M1; 共享总线 |
| 4 | `VCC_5V0` | — | 5V 电源 | 电源，不是GPIO |
| 5 | `I2C3_SCL_M1` | `GPIO3_B7`; gpio3 / 15 | 3.3V直连 | I2C3 SCL M1; 共享总线 |
| 6 | `GND` | — | GND | 地线，不是GPIO |
| 7 | `GPIO4_C6_3V3` | `GPIO4_C6`; gpio4 / 22 | 1.8V → U33 A3/B3 → 3.3V | GPIO候选 |
| 8 | `UART2_TX_DEBUG_PORT` | `GPIO0_B5`; gpio0 / 13 | 3.3V直连 | UART2 TX M0 （调试） |
| 9 | `GND` | — | GND | 地线，不是GPIO |
| 10 | `UART2_RX_DEBUG_PORT` | `GPIO0_B6`; gpio0 / 14 | 3.3V直连 | UART2 RX M0 （调试） |
| 11 | `GPIO0_C0` | `GPIO0_C0`; gpio0 / 16 | 3.3V直连 | PWM1 M0 |
| 12 | `GPIO1_A7_u_3V3` | `GPIO1_A7`; gpio1 / 7 | 1.8V → U34 A8/B8 → 3.3V | PWM3 IR M3 |
| 13 | `GPIO2_B7_3V3` | `GPIO2_B7`; gpio2 / 15 | 1.8V → U33 A5/B5 → 3.3V; R226 22Ω | GPIO候选 |
| 14 | `GND` | — | GND | 地线，不是GPIO |
| 15 | `GPIO1_C6_3V3` | `GPIO1_C6`; gpio1 / 22 | 1.8V → U34 A3/B3 → 3.3V | GPIO候选 |
| 16 | `GPIO1_B0_u_3V3` | `GPIO1_B0`; gpio1 / 8 | 1.8V → U34 A2/B2 → 3.3V | GPIO候选 |
| 17 | `EXT_3V3` | — | 3.3V 电源 | 电源，不是GPIO |
| 18 | `GPIO1_B4_u_3V3` | `GPIO1_B4`; gpio1 / 12 | 1.8V → U34 A7/B7 → 3.3V | GPIO候选 |
| 19 | `GPIO2_C2_3V3` | `GPIO2_C2`; gpio2 / 18 | 1.8V → U33 A8/B8 → 3.3V; R224 22Ω | SPI1 MOSI M0 |
| 20 | `GND` | — | GND | 地线，不是GPIO |
| 21 | `GPIO2_C1_3V3` | `GPIO2_C1`; gpio2 / 17 | 1.8V → U33 A7/B7 → 3.3V; R223 22Ω | SPI1 MISO M0 |
| 22 | `GPIO1_B5_u_3V3` | `GPIO1_B5`; gpio1 / 13 | 1.8V → U34 A5/B5 → 3.3V | GPIO候选 |
| 23 | `GPIO2_C0_3V3` | `GPIO2_C0`; gpio2 / 16 | 1.8V → U33 A6/B6 → 3.3V; R222 22Ω | SPI1 CLK M0; 与40脚同网，不能独立控制 |
| 24 | `nPi_GPIO8` | `GPIO2_C3`; gpio2 / 19 | 1.8V → U32 A2/B2 → 3.3V; R225 22Ω, R471 22Ω | SPI1 CS0 M0; R471已装，R472不装(DNP) |
| 25 | `GND` | — | GND | 地线，不是GPIO |
| 26 | `GPIO1_B3_3V3` | `GPIO1_B3`; gpio1 / 11 | 1.8V → U32 A6/B6 → 3.3V | GPIO候选; 不是SPI1 CS1 |
| 27 | `I2C6_SDA_3V3` | `GPIO0_C7`; gpio0 / 23 | 3.3V直连 | I2C6 SDA M0; 共享总线 |
| 28 | `I2C6_SCL_3V3` | `GPIO0_D0`; gpio0 / 24 | 3.3V直连 | I2C6 SCL M0; 共享总线 |
| 29 | `GPIO0_C5_u` | `GPIO0_C5`; gpio0 / 21 | 3.3V直连 | PWM4 M0 |
| 30 | `GND` | — | GND | 地线，不是GPIO |
| 31 | `GPIO4_B0` | `GPIO4_B0`; gpio4 / 8 | 3.3V直连 | GPIO候选 |
| 32 | `GPIO1_D7_u_3V3` | `GPIO1_D7`; gpio1 / 31 | 1.8V → U34 A4/B4 → 3.3V | GPIO候选 |
| 33 | `UART4_TX_M0_3V3` | `GPIO1_D2`; gpio1 / 26 | 1.8V → U32 A7/B7 → 3.3V | UART4 TX M0; PWM0 M1 |
| 34 | `GND` | — | GND | 地线，不是GPIO |
| 35 | `UART4_RX_M0_3V3` | `GPIO1_D3`; gpio1 / 27 | 1.8V → U32 A8/B8 → 3.3V; R233 100Ω | UART4 RX M0; PWM1 M1 |
| 36 | `GPIO1_B7_u_3V3` | `GPIO1_B7`; gpio1 / 15 | 1.8V → U32 A5/B5 → 3.3V | GPIO候选 |
| 37 | `GPIO1_D6_u_3V3` | `GPIO1_D6`; gpio1 / 30 | 1.8V → U34 A6/B6 → 3.3V; R234 100Ω | GPIO候选 |
| 38 | `GPIO0_C4` | `GPIO0_C4`; gpio0 / 20 | 3.3V直连 | PWM2 M0; 同一控制器通过M2用于风扇 |
| 39 | `GND` | — | GND | 地线，不是GPIO |
| 40 | `GPIO2_C0_3V3` | `GPIO2_C0`; gpio2 / 16 | 1.8V → U33 A6/B6 → 3.3V; R222 22Ω | SPI1 CLK M0; 与23脚同网，不能独立控制 |

## 电平路径与连线说明

- U32/U33/U34 均为 TXS0108ERGYR：VCCA=`VCC_1V8_S0`，VCCB=`EXT_3V3`。GPIO1_C6 属于固定1.8V的 VCCIO1；GPIO2_B7/C0/C1/C2/C3、GPIO4_C6 属于固定1.8V的 VCCIO3；本板相关 VCCIO4 pad 供电也是1.8V。PMUIO2 经 R199 接3.3V；相关 VCCIO5/VCCIO6 pad 在本板也供电3.3V。不能把 SoC 电压直接当成排针电压。
- **J10-15更正：** U34 A3 为封装4脚、B3为封装17脚，旧资料误写为5脚/16脚。SoC pad 仍为 GPIO1_C6、gpio1/`fec20000`、局部offset22，GPIO映射未变。
- **J10-24：** `nPi_GPIO8` 经已装 R471(22Ω)、R225(22Ω)、U32 B2/A2 到 GPIO2_C3；到 GPIO0_C6 的另一支路 R472(22Ω) 标为 **DNP不装**，不能算第二条有效路径。`nPi_GPIO8` 不是 Rockchip GPIO 或 line offset。返修过的板需检查实际装配。
- 原理图的 ESD 保护不能证明5V容忍。安全输入上限、单针输出电流、外设实际可用电源电流仍未确认；供电轨设计标注不等于外设可用功率承诺。静态表本身不授权硬件操作。

## 接口分组与冲突

- **I2C3 M1，3/5脚：** SDA=GPIO3_C0，SCL=GPIO3_B7；R465/R466 为到 `VCC_3V3_S0` 的2.2k上拉（第15页），同时连接 USB hub 控制端（第22页）和摄像头连接器（第29页）。先核对当前 adapter、外设及内核 client，不把活动共享总线改成推挽 GPIO，也不盲目全总线扫描。
- **I2C6 M0，27/28脚：** SDA=GPIO0_C7，SCL=GPIO0_D0；R5067/R5068 为到 `VCC_3V3_S3` 的2.2k上拉（第7页）。总线上有 Type-C FUSB302(0x22)、PCF8563 RTC(0x51) 及其他连接器，并非外接传感器独占。运行时解析实际 adapter，不假定 `/dev/i2c-N` 编号。
- **SPI1 M0：** MOSI=19、MISO=21、CLK=23、CS0=24，并与第33页扩展接口共享。40脚与23脚同网，也是 CLK，不能独立控制。26脚是 GPIO1_B3，**不是 SPI1 CS1**；pinctrl 源码中 CS1 M0 位于 GPIO2_C4。缓存板级 DTS 启用了 SPI1/spidev，不代表当前设备配置。
- **UART：** 8/10脚为 UART2 M0 TX/RX 调试网络，改复用前检查 console/debugger；33/35脚为经 U32 转换的 UART4 M0 TX/RX，RX还有 R233 100Ω。识别实际 tty、控制器及占用；标签不代表串口已经启用。
- **PWM候选：** 11脚PWM1 M0、12脚PWM3 IR M3、29脚PWM4 M0、33脚PWM0 M1、35脚PWM1 M1、38脚PWM2 M0。11/35的PWM1是同一控制器的不同路由。缓存 vendor DTS 将 GPIO4_C2 上的 PWM2 M2 用于散热风扇，38脚的PWM2 M0不是独立控制器，不能通过停用散热直接启用；GPIO4_C2也不是J10-38。

## 运行时解析 Linux 身份

YAML 为每个原理图信号给出 DT 控制器节点：gpio0=`fd8a0000`、gpio1=`fec20000`、gpio2=`fec30000`、gpio3=`fec40000`、gpio4=`fec50000`，各32条局部line。根据当前 DT `of_node`、label、line count 解析实际 `/dev/gpiochip*`，不能固定编号。bank内offset=`8×组(A=0,B=1,C=2,D=3)+bit`，15脚C6是22，不是pinctrl调试索引54。

28个信号位置中，缓存 vendor DTS 定义了26个同编号 `PIN_*` 标签，其中24处与原理图不符，仅 PIN_8/PIN_10 一致；PIN_22/PIN_37 未定义。例如 `PIN_15` 实际标在 GPIO3_C0，而物理 J10-15 是 GPIO1_C6；GPIO3_C0 在原理图中对应 J10-3。不能用 `gpiofind PIN_15` 代替板级连线依据。申请line前检查当前mux、consumer/owner、权限及接线。释放成input不保证电压为0V。

## 来源摘图

[官方V1.0原理图](https://files.seeedstudio.com/wiki/reComputer_RK/Documents/recomputer_rk3588/RECOMPUTER_RK3588_V10_0119.pdf)：第7/11/15/28页及共享走线第22/29/33页。哈希、适用范围、RK3588 pinctrl/DTS缓存位置见[来源索引](../../../../../sources/index.yaml)。缓存目录名虽然含 `rk3576`，本次审阅的文件明确为 `rk3588*.dts[i]`，没有复用RK3576物理针脚表。

![J10全部排针及R471/R472，第28页](assets/schematic-sheet28-j10.png)

![U32/U33/U34电平路径，第28页](assets/schematic-sheet28-translators.png)

用户接线时可按[接线图指南与AHT20示例](../../../../../common/wiring-diagrams.zh-CN.md)给出本板的物理针脚定位和逐线连接图。

排针定位图必须按[wiring-layout.yaml](wiring-layout.yaml)记录的主板视角：元件面朝上、排针在上边缘，上排39→1、下排40→2，1/2脚在右端；不能按通用竖向表替代。
