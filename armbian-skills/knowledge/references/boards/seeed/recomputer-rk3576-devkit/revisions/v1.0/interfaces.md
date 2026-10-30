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

# V1.0 interface sources and Linux-label differences

The official schematic and vendor source mapping differ; see [complete J3 mapping](schematic-mapping.md). Retain vendor gpio-line-names as source claims explaining why labels cannot directly identify physical pins, not as corrected pinout data.

| J3 label claim | Vendor line-name pad | Schematic J3 pad | Match |
|---|---|---|---|
| 3 | `GPIO1_C7` | `GPIO4_B4` | No |
| 5 | `GPIO1_C6` | `GPIO4_B5` | No |
| 7 | `GPIO1_C3` | `GPIO3_C6` | No |
| 8 | `GPIO0_D4` | `GPIO0_D4` | Yes |
| 10 | `GPIO0_D5` | `GPIO0_D5` | Yes |
| 11 | `GPIO1_C4` | `GPIO4_A6` | No |
| 12 | `GPIO1_D1` | `GPIO4_A0` | No |
| 13 | `GPIO2_C0` | `GPIO4_A4` | No |
| 15 | `GPIO1_C5` | `GPIO2_B5` | No |
| 16 | `GPIO2_B6` | `GPIO4_A1` | No |
| 18 | `GPIO2_B7` | `GPIO0_C6` | No |
| 19 | `GPIO1_B5` | `GPIO3_D6` | No |
| 21 | `GPIO1_B6` | `GPIO3_D5` | No |
| 22 | `GPIO2_D7` | `GPIO2_B1` | No |
| 23 | `GPIO1_B4` | `GPIO3_D4` | No |
| 24 | `GPIO1_B7` | `GPIO3_D7` | No |
| 26 | `GPIO1_C0` | `GPIO0_C7` | No |
| 27 | `GPIO4_C7` | `GPIO3_B7` | No |
| 28 | `GPIO4_C6` | `GPIO3_C0` | No |
| 29 | `GPIO3_A2` | `GPIO3_C1` | No |
| 31 | `GPIO1_C1` | `GPIO3_C4` | No |
| 32 | `GPIO1_D5` | `GPIO0_D3` | No |
| 33 | `GPIO1_C2` | `GPIO4_A7` | No |
| 35 | `GPIO1_D2` | `GPIO0_C4` | No |
| 36 | `GPIO1_D4` | `GPIO4_C7` | No |
| 37 | `GPIO3_A3` | `GPIO0_C5` | No |
| 38 | `GPIO1_D3` | `GPIO3_A3` | No |
| 40 | `GPIO1_D0` | `GPIO3_A2` | No |

Of 28 signal labels, only physical pins 8/10 match. Resolve real pins from the schematic and current controller identity rather than assuming a Linux label's pad corresponds to the same J3 number.

[interfaces.yaml](interfaces.yaml) retains source labels/comparisons; [schematic-mapping.yaml](schematic-mapping.yaml) contains40-pin nets, local offsets, DT controller identity, translation paths, and constraints; [official-pinout.yaml](official-pinout.yaml) preserves original image labels, including pin 26's SPI discrepancy.

Preserve protections for onboard expanders, reset/power, LEDs, and fans. Pins 27/28 use shared I2C4: no scanning or forced access. Pins 8/10 are debug UART. Pin 26 cannot be treated as SPI3 CS0 from its image label, nor can a fan PWM node stand in for pins 32/33.

For user wiring, see [diagram guidance and AHT20 examples](../../../../../common/wiring-diagrams.md) for physical header locations and explicit wire endpoints on this board.

Pin locators must follow the board view in [wiring-layout.yaml](wiring-layout.yaml): component side facing viewer, header at top, upper row39→1 and lower row40→2 left-to-right, pins1/2 at right. Do not substitute a generic vertical pin grid.
