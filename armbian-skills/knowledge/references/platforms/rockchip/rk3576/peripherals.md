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

# RK3576 peripheral candidates

This reference covers host-cached vendor kernel source, not the target runtime. Controller pinctrl claims live in pinctrl-claims.yaml; board references determine connector routing.

| Capability | Host source evidence | Confirm before use |
|---|---|---|
| GPIO | gpio0-4, PCA9535, GPIO_CDEV in cached.config | Actual controller, line/mux, consumer, board electrical conditions |
| I2C | I2C_CHARDEV; I2C3 overlay; internal I2C4 devices | External routing; no internal-bus scans or forced driver-address access |
| UART | UART3/UART5 overlays; UART4 for BT | Serial aliases/console/getty, TTL voltage, peer protocol |
| SPI | SPI_SPIDEV; spi3/spidev and m1 pinctrl | Current node, shared modules, CS, mode, speed |
| CAN | CAN_ROCKCHIP=m; CAN0/1 overlays | External transceiver, termination, electrical conditions, bitrate, test network |
| PWM | pwm2_8ch_6 overlay; onboard pwm-fan | Customer channel versus thermal control; do not seize the fan |
| Camera | RKISP/RKCIF; cam0/1 v2/v3 overlays | Sensor, media graph, IQ/3A, frame format |

SPI3 and UART5 m0 share source pads; the UART5 overlay explicitly disables SPI3. Node/overlay presence does not establish target installation/enablement. CAN overlays do not prove a directly usable bus transceiver is present.
