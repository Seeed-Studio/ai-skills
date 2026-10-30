---
schema_version: '1'
id: platform.rockchip.rk3576.peripherals
kind: platform_guide
applies_to:
  soc_ids:
  - rockchip.rk3576
required_refs:
- platform.rockchip.rk3576.pinctrl-claims
preconditions: []
refines: []
excludes: []
related: []
sources:
- source.cached-vendor-dts
- source.cached-pinctrl
- source.local-kernel-config
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](peripherals.md) | [简体中文](peripherals.zh-CN.md)

# RK3576 外设接入候选

本资料以 Host 缓存 vendor kernel 为范围，不能代替目标 runtime。控制器 pinctrl 独立保存于 `pinctrl-claims.yaml`，物理连接器映射由板级资料决定。

| 能力 | Host 源码证据 | 应用前要确认 |
|---|---|---|
| GPIO | gpio0-4、PCA9535、GPIO_CDEV（缓存 .config） | 实际控制器、line/mux、consumer、板级电气 |
| I2C | I2C_CHARDEV；I2C3 overlay；I2C4 有内部器件 | 仅识别外部总线，不扫描内部总线或强制访问驱动地址 |
| UART | UART3/UART5 overlays；UART4 用于 BT | serial alias/console/getty、TTL 电压、对端协议 |
| SPI | SPI_SPIDEV；spi3/spidev、m1 pinctrl | 当前设备节点、共享模块、CS、模式和速率 |
| CAN | CAN_ROCKCHIP=m；CAN0/1 overlays | 外部收发器、终端、电气、接口 bitrate 和测试网络 |
| PWM | pwm2_8ch_6 overlay；板载 pwm-fan | 区分客户通道与热管理，运行中不抢占风扇 |
| Camera | RKISP/RKCIF、cam0/1 的 v2/v3 overlays | 实际 sensor、media graph、IQ/3A 与帧格式 |

SPI3 与 UART5 m0 在源码中共用 pad，UART5 overlay 显式禁用 SPI3。节点/overlay 存在不代表目标镜像已经安装或启用；CAN overlay 也不证明板上有客户可直接连接的 CAN 电气收发器。
