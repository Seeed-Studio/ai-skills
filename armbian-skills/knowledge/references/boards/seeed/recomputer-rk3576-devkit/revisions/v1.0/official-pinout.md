---
schema_version: '1'
id: board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout.guide
kind: board_guide
applies_to:
  board_ids:
  - seeed.recomputer-rk3576-devkit
  hardware_revisions:
  - v1.0
required_refs:
- board.seeed.recomputer-rk3576-devkit.v1.0.official-pinout
- board.seeed.recomputer-rk3576-devkit.v1.0.interfaces
preconditions: []
refines: []
excludes: []
related:
- board.seeed.recomputer-rk3576-devkit.v1.0.schematic-mapping
sources:
- source.seeed-rk3576-official-40pin-image
validation_refs: []
maturity: documented
owner: armbian-platform-maintainers
updated_at: '2026-10-19'
---

[English](official-pinout.md) | [简体中文](official-pinout.zh-CN.md)

# Official 40-pin labels

Applies to the RK3576-20/30 full-system DevKit, not Module Dev Kit. This is a visual transcription of image29.png from Seeed's official interface page. Preserve the original labels without inferring Linux GPIO numbers. The image does not state PCB revision; placing it in the V1.0 profile associates references but does not independently prove a target revision.

[Official interface guide](https://sensecraft.seeed.cc/ai-lab/en/tutorials/rk/edge-ai-computer/rk3576/interface-usage-guidelines/use-recomputer-rk3576-hardware-interfaces-and-fan-control) · [Original image](https://files.seeedstudio.com/wiki/reComputer_RK/ai_lab/tutorials/image29.png) · [Structured table](official-pinout.yaml)

![Official 40-pin definition diagram](assets/40pin-official.png)

## Orientation

The official photo shows the component side with the40-pin header at the top. The upper odd row runs39→1 left-to-right; the lower even row runs40→2, placing1/2 at the right end. Confirm actual orientation and pin 1 on the device.

This lookup table is sorted1→40, not laid out in the image's left-to-right order.

| Odd pin | Official label | Even pin | Official label |
|---|---|---|---|
| 1 | `3.3V` | 2 | `5V` |
| 3 | `SDA` | 4 | `5V` |
| 5 | `SCL` | 6 | `GND` |
| 7 | `GPIO` | 8 | `DEBUG_TX` |
| 9 | `GND` | 10 | `DEBUG_RX` |
| 11 | `CANRX/GPIO` | 12 | `UART_TX/GPIO` |
| 13 | `CANTX/GPIO` | 14 | `GND` |
| 15 | `GPIO` | 16 | `UART_RX/GPIO` |
| 17 | `3.3V` | 18 | `GPIO` |
| 19 | `SPI_MOSI` | 20 | `GND` |
| 21 | `SPI_MISO` | 22 | `GPIO` |
| 23 | `SPI_CLK` | 24 | `SPI_CSN/GPIO` |
| 25 | `GND` | 26 | `SPI_CSN/GPIO` |
| 27 | `EEPROM_SDA` | 28 | `EEPROM_SCL` |
| 29 | `GPIO` | 30 | `GND` |
| 31 | `GPIO` | 32 | `GPIO/PWM` |
| 33 | `PWM` | 34 | `GND` |
| 35 | `GPIO` | 36 | `GPIO` |
| 37 | `GPIO` | 38 | `CANRX/GPIO` |
| 39 | `GND` | 40 | `CANTX/GPIO` |

## What the labels establish

- Power:1/17 label3.3V,2/4 label5V, and 6/9/14/20/25/30/34/39 labelGND. These are documented claims, not present electrical measurements. A 5V power pin does not establish5V-tolerant GPIO.
- Communication:3/5 are SDA/SCL;8/10 DEBUG_TX/RX;12/16 UART_TX/RX;19/21/23 SPI_MOSI/MISO/CLK;24/26 both SPI_CSN/GPIO.11/13 and 38/40 label CAN RX/TX.
- PWM:32 labels GPIO/PWM and 33 labels PWM. The image identifies no controller/channel and cannot establish two independent PWM channels.
-27/28 label EEPROM_SDA/SCL; the image alone does not identify bus number, internal sharing, or customer I2C availability.
- CAN/UART/I2C labels omit controller numbers, and SPI_CSN labels omit CS numbers. Do not assign CAN0/1, UART3/5, or CS0/1 from ordering. CAN TX/RX are not CAN_H/CAN_L.

## Schematic additions and discrepancies

The table preserves original image labels. [V1.0 J3 schematic mapping](schematic-mapping.md) separately documents all 40 nets,28 signal pads, banks/local offsets, mux candidates, and translators. Do not attribute those additional facts to the image itself.

- Pin 26: image SPI_CSN/GPIO, schematic GPIO0_C7, not SPI3 CS0. Pin 24 is SPI3 m1 CS1.
-27/28: schematic I2C4 m3, shared with onboard devices. EEPROM labels do not establish an independent customer bus.
-32/33: documented candidates PWM2_CH0_M0/PWM2_CH6_M0, not current enablement.

## Combining Linux information

The28 PIN_* entries in [interface conflicts](interfaces.md) are source label claims. Do not import their banks/offsets into this physical table. Check consumer/mux on the actual mapped pad.

Official labels describe physical positions; runtime inspection describes current enablement. Use schematic mapping for pin-to-net and power domains, and confirm actual orientation, wiring, electrical conditions, and load. This page does not authorize overlays or output.
