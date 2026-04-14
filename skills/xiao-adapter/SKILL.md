---
name: xiao-adapter
description: Guide for adapting Seeed Studio XIAO series development boards to new MCU chips across Arduino, PlatformIO, and MicroPython platforms. Use when the user asks to adapt a new MCU chip to XIAO board, add Arduino BSP support for XIAO-XXX, create PlatformIO board definition for XIAO, write MicroPython porting guide for XIAO, or generate board configuration files (boards.txt, pins_arduino.h, platformio.ini, mpconfigboard.h, pins.csv).
---

# XIAO Adapter

Adapt new MCU chips to Seeed Studio XIAO series development boards. This skill provides workflows for three platforms, each following: **pull base project -> generate/modify config -> compile and verify**.

## Platform Selection

Determine the target platform from user context, then read the corresponding reference:

| Platform | Reference | Key Outputs |
|---|---|---|
| Arduino | [references/arduino-bsp.md](references/arduino-bsp.md) | `boards.txt`, `pins_arduino.h`, variant files |
| PlatformIO | [references/platformio.md](references/platformio.md) | `platformio.ini`, board JSON definition |
| MicroPython | [references/micropython.md](references/micropython.md) | `mpconfigboard.h`, `pins.csv`, `board_init.c` |

If the user requests multiple platforms, process each independently.

## Naming Conventions

All XIAO board identifiers follow this pattern:

```
seeed_xiao_<chip_series>
```

Examples: `seeed_xiao_rp2040`, `seeed_xiao_esp32c3`, `seeed_xiao_stm32f103`

## Workflow Overview

Two entry paths: **Schematic-Driven** (auto-extract from schematic) or **Manual** (user provides chip info).

### Path A: Schematic-Driven Workflow (Preferred)

When the user provides a KiCad/Cadence schematic project, use `schematic-analyzer` to extract all chip and pin information automatically.

**Prerequisite**: `schematic-analyzer` skill and `python3` must be available. KiCad projects also require `kicad-cli`.

#### A1. Identify the MCU from schematic

```bash
# Overview to find core component candidates
python <schematic-analyzer>/scripts/schematic-cli.py overview <project_path>

# Query the MCU component (e.g., U1, U10 — identified from overview)
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --component <MCU_REF> \
  | python -c "import sys,json; d=json.load(sys.stdin); print(f\"MCU: {d['value']}, MPN: {d.get('mpn')}\")"
```

If the MCU part number is unclear, escalate to `pcbparts` MCP or `ee-datasheet-master`.

#### A2. Extract pin mapping from schematic

Query each XIAO castellated pad net to determine MCU pin assignments:

```bash
# Find all nets connected to the MCU
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --component <MCU_REF> \
  | python -c "import sys,json; d=json.load(sys.stdin); print([n['name'] for n in d['nets']])"

# Trace specific interface nets (I2C, SPI, UART, USB, LED)
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "SDA|SCL|I2C"
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "MOSI|MISO|SCK|SS"
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "TX|RX|UART"
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "USB_DP|USB_DN|D\+|D-"
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "LED"
```

For each net, trace pins to get the MCU-side pin:

```bash
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net <NET_NAME> \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(f\"{p['ref']}.{p['pin']}\") for p in d['pins'] if p['ref']=='<MCU_REF>']"
```

#### A3. Extract peripheral configuration

Query debug interface, crystal/oscillator, and power pins:

```bash
# Debug interface (SWD/JTAG)
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "SWD|SWCLK|SWDIO|JTAG|TCK|TMS|TDI|TDO"

# Crystal/oscillator
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --component --match "XTAL|CRYSTAL|OSC"

# Power (VDD, VCC, 3V3)
python <schematic-analyzer>/scripts/schematic-cli.py query <project_path> --net --match "VDD|VCC|3V3|VBAT"
```

#### A4. Build chip info summary

Compile all extracted data into a structured summary:

```
MCU: <model> (<core architecture>)
MPN: <manufacturer part number>
Flash: <size>  RAM: <size>
Clock: <max_freq> (crystal: <xtal_freq> if found)
Debug: <SWD/JTAG/USB-Serial>
LED pin: <MCU pin for onboard LED>
Pin mapping:
  D0  (UART RX / A0)  -> <MCU_PIN>
  D1  (UART TX / A1)  -> <MCU_PIN>
  D2  (SPI CS  / A2)  -> <MCU_PIN>
  ...
  SDA (I2C)           -> <MCU_PIN>
  SCL (I2C)           -> <MCU_PIN>
  MOSI                -> <MCU_PIN>
  MISO                -> <MCU_PIN>
  SCK                 -> <MCU_PIN>
```

If any required field is missing from schematic analysis (e.g., Flash/RAM size from the schematic alone), consult the datasheet via `ee-datasheet-master` or ask the user.

#### A5. Proceed to Step 2 (Pull Base Project)

Use the extracted chip info to select the correct base repository and continue with the standard workflow below.

### Path B: Manual Workflow

When no schematic is available, gather chip information from the user or datasheet:

- MCU model and core (ARM Cortex-M0/M3/M4/M33, RISC-V, Xtensa, etc.)
- Flash size / RAM size
- Clock frequency (max and default)
- Package type and pin count
- Debug interface (SWD, JTAG, USB-Serial)
- Key peripherals (SPI, I2C, UART, ADC, PWM, USB)
- USB VID/PID (must be provided by user — contact Seeed internal team to apply, never fabricate values)

If information is incomplete, ask the user for the missing items.

### Step 2: Pull Base Project

Clone the appropriate base repository for the target platform and chip architecture. See each platform reference for specific commands.

### Step 3: Generate Configuration

Follow the platform-specific reference to generate all required config files. Place generated files in the correct directory structure. When using schematic-driven path, populate pin mappings from the extraction results (A4).

### Step 4: Compile and Verify

Use the platform toolchain to compile. Fix errors iteratively. Run the standard test suite (see below).

## Standard Test Checklist

After successful compilation, verify on real hardware with these tests in order:

1. **Blink** — Toggle onboard LED, confirm timing matches clock config
2. **Serial Echo** — Loopback TX->RX or echo via USB serial, confirm baudrate
3. **GPIO Input** — Read button/switch state, print to serial
4. **I2C Scanner** — Enumerate devices on I2C bus
5. **SPI Loopback** — MOSI->MISO short, verify SPI transmit/receive
6. **ADC Read** — Read analog pin with floating/noise check
7. **PWM Output** — Output PWM on LED pin, confirm duty cycle control
8. **USB (if applicable)** — Confirm USB CDC serial or HID enumeration

## Seeed XIAO Hardware Reference

Typical XIAO form factor:
- 14-pin castellated pad design (7 per side)
- USB Type-C connector
- Onboard LED (usually on a specific GPIO, varies by chip)
- Reset button
- Size: 20mm x 17.5mm

Common pin mapping across XIAO variants:

| Function | Typical Pin | Notes |
|---|---|---|
| LED | D13 / GPIO depend on chip | Active LOW in most XIAO designs |
| UART TX | D1 | |
| UART RX | D0 | |
| I2C SDA | D4 | |
| I2C SCL | D5 | |
| SPI MOSI | D10 | |
| SPI MISO | D9 | |
| SPI SCK | D8 | |
| SPI CS | D2 | |
| A0 / ADC | A0 / D0 (shared) | |
| A1 / ADC | A1 / D1 (shared) | |
| A2 / ADC | A2 / D2 (shared) | |
| A3 / ADC | A3 / D3 (shared) |

Note: Exact pin assignments depend on the target MCU's pin mux capabilities. Always cross-reference with the chip datasheet and schematic.
