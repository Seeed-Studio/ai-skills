# MicroPython Porting for XIAO

## Table of Contents

1. [Repository Setup](#1-repository-setup)
2. [Port Selection](#2-port-selection)
3. [Board Config Files](#3-board-config-files)
4. [Pin Definition](#4-pin-definition)
5. [Build and Flash](#5-build-and-flash)
6. [Testing with pyboard](#6-testing-with-pyboard)
7. [Common Issues](#7-common-issues)

---

## 1. Repository Setup

Seeed maintains a wrapper repository with MicroPython as a submodule:

```bash
git clone https://github.com/Seeed-Studio/micropython-seeed-boards.git
cd micropython-seeed-boards
git submodule update --init --recursive
```

Repository structure:

```
micropython-seeed-boards/
├── boards/                          # Board configurations
│   ├── seeed/                       # Full board definitions (Zephyr, Renesas)
│   │   ├── xiao_nrf54l15/          # Zephyr board port (DTS, defconfig, board.yml)
│   │   └── xiao_ra4m1/             # Renesas RA board (mpconfigboard.h, pins.csv)
│   ├── xiao_mg24.conf              # Flat Kconfig overlay (Zephyr)
│   ├── xiao_mg24.overlay           # Flat device tree overlay (Zephyr)
│   └── pm_static_xiao_*.yml        # Memory partition maps (Zephyr)
├── lib/
│   └── micropython/                 # Upstream MicroPython (submodule)
│       └── ports/
│           ├── zephyr/              # Zephyr RTOS port
│           ├── esp32/               # ESP-IDF port
│           ├── renesas-ra/          # Renesas RA port
│           ├── stm32/               # STM32/shared ARM Cortex-M port
│           └── rp2/                 # RP2040 port
├── src/cmodules/                    # Custom C modules (modadc, modrtc, etc.)
├── tools/                           # Board-specific flash tools
└── example/                         # Example scripts
```

## 2. Port Selection

MicroPython supports XIAO boards through multiple ports, each with different config styles:

| Architecture | MicroPython Port | Config Style | Board Dir | Architecture Reference |
|---|---|---|---|---|
| nRF54L15 / nRF52840 / MG24 | Zephyr | `.conf` + `.overlay` + Zephyr board port | `boards/seeed/xiao_*/` | [arch/nrf52.md](arch/nrf52.md) |
| ESP32-C3/C6/S3 | ESP-IDF | Traditional | `boards/seeed/xiao_esp32*/` | [arch/esp32.md](arch/esp32.md) |
| RA4M1 | renesas-ra | Traditional | `boards/seeed/xiao_ra4m1/` | [arch/stm32.md](arch/stm32.md) |
| SAMD21 | stm32 | Traditional | `boards/seeed/xiao_samd*/` | [arch/samd21.md](arch/samd21.md) |
| RP2040 | rp2 | CMake | `boards/seeed/xiao_rp2040/` | [arch/rp2040.md](arch/rp2040.md) |

> **Important**: Architecture reference files contain MicroPython-specific sections with pin naming, flash tools, and port-specific notes.

## 3. Board Config Files

### Track A: Zephyr (nRF54L15, MG24, nRF52840)

Zephyr boards use **two sets of files**: a full Zephyr board port under `boards/seeed/<board>/` plus MicroPython-specific overlay/conf files in the flat `boards/` directory.

**Full Zephyr board port** (`boards/seeed/xiao_<board>/`):

| File | Purpose |
|---|---|
| `board.yml` | Board metadata (name, vendor, SoC) |
| `board.cmake` | Flash runner config |
| `<board>_<soc>_<cpu>.dts` | Main device tree file |
| `<board>_common.dtsi` | Shared device tree include (LEDs, buttons, peripherals) |
| `<board>-pinctrl.dtsi` | Pin control definitions |
| `seeed_xiao_connector.dtsi` | XIAO connector GPIO map (D0-D15) |
| `<board>_<soc>_<cpu>_defconfig` | Zephyr defconfig |
| `Kconfig.defconfig` | Conditional Kconfig defaults |

**MicroPython overlay files** (flat in `boards/`):

| File | Purpose |
|---|---|
| `xiao_<board>_<soc>_<cpu>.conf` | Kconfig overrides for MicroPython (BT, flash, filesystem, etc.) |
| `xiao_<board>_<soc>_<cpu>.overlay` | Device tree overlay (RTC, ADC channels, PWM, filesystem) |
| `pm_static_xiao_<board>_*.yml` | Static memory partition map |

Example `board.yml`:
```yaml
board:
  name: xiao_nrf54l15
  full_name: XIAO NRF54L15
  vendor: seeed
  socs:
  - name: nrf54l15
    variants:
    - name: xip
      cpucluster: cpuflpr
```

Example `.conf` snippet:
```
CONFIG_SPI=y
CONFIG_ADC=y
CONFIG_PWM=y
CONFIG_BT=y
CONFIG_FLASH=y
CONFIG_FLASH_MAP=y
CONFIG_FILE_SYSTEM=y
CONFIG_FILE_SYSTEM_LITTLEFS=y
```

Example `.overlay` snippet:
```dts
/ {
    zephyr,user {
        io-channels = <&adc 0>, <&adc 1>, <&adc 2>;
    };
};
&xiao_i2c {
    status = "okay";
};
```

### Track B: Traditional (ESP32, RA4M1, SAMD21, STM32)

Traditional boards use MicroPython's native board config format under `boards/seeed/xiao_<board>/`:

| File | Purpose |
|---|---|
| `mpconfigboard.h` | Board-level MicroPython C config |
| `mpconfigboard.mk` | Build variables |
| `pins.csv` | Pin name mapping |
| `manifest.py` | Frozen module manifest |
| `board.json` | Board metadata |
| `<board>.ld` | Linker script (optional, port-dependent) |

#### mpconfigboard.h

```c
#define MICROPY_HW_BOARD_NAME       "SEEED_XIAO_<CHIP>"
#define MICROPY_HW_MCU_NAME         "<MCU_NAME>"
#define MICROPY_HW_MCU_SYSCLK       <FREQ>
#define MICROPY_HW_MCU_PCLK         <FREQ>

// UART
#define MICROPY_HW_UART0_TX        (pin_<TX_PIN>)
#define MICROPY_HW_UART0_RX        (pin_<RX_PIN>)

// I2C
#define MICROPY_HW_I2C0_SCL        (pin_<SCL_PIN>)
#define MICROPY_HW_I2C0_SDA        (pin_<SDA_PIN>)

// SPI
#define MICROPY_HW_SPI0_SCK        (pin_<SCK_PIN>)
#define MICROPY_HW_SPI0_MOSI       (pin_<MOSI_PIN>)
#define MICROPY_HW_SPI0_MISO       (pin_<MISO_PIN>)

// LED (active LOW on most XIAO boards)
#define MICROPY_HW_LED1             (pin_<LED_PIN>)
#define MICROPY_HW_LED_ON(pin)      mp_hal_pin_low(pin)
#define MICROPY_HW_LED_OFF(pin)     mp_hal_pin_high(pin)

// USB
#define MICROPY_HW_USB_VID         <USER_PROVIDED_VID>
#define MICROPY_HW_USB_PID         <USER_PROVIDED_PID>
#define MICROPY_HW_USB_CDC         (1)
#define MICROPY_HW_ENABLE_USBDEV   (1)

// Feature enables
#define MICROPY_HW_ENABLE_RTC       (1)
#define MICROPY_HW_ENABLE_ADC       (1)
#define MICROPY_HW_HAS_FLASH        (1)
#define MICROPY_HW_ENABLE_INTERNAL_FLASH_STORAGE (1)
```

#### mpconfigboard.mk

```makefile
CMSIS_MCU = <MCU>
MCU_SERIES = <series>
LD_FILES = boards/<board>/<board>.ld

MICROPY_VFS_LFS2 = 0
MICROPY_VFS_FAT = 1

FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py
```

#### manifest.py

```python
include("$(MPY_DIR)/extmod/asyncio")
```

#### board.json

```json
{
    "deploy": ["../deploy.md"],
    "mcu": "<mcu>",
    "product": "seeed-xiao_<board>",
    "url": "https://wiki.seeedstudio.com/XIAO_<CHIP>/",
    "vendor": "Seeed Studio"
}
```

## 4. Pin Definition

### Traditional: pins.csv

Format: `logical_name,cpu_pin`

```
D0,<MCU_PIN_D0>
D1,<MCU_PIN_D1>
D2,<MCU_PIN_D2>
D3,<MCU_PIN_D3>
D4,<MCU_PIN_D4>
D5,<MCU_PIN_D5>
D6,<MCU_PIN_D6>
D7,<MCU_PIN_D7>
D8,<MCU_PIN_D8>
D9,<MCU_PIN_D9>
D10,<MCU_PIN_D10>
LED,<MCU_PIN_LED>
```

Pin naming is architecture-specific — see [architecture reference](arch/) for the correct format (e.g., `PA10` for SAMD21/STM32, `P302` for RA4M1, `GPIO5` for ESP32).

### Zephyr: Device tree overlay

Pins are defined in the device tree files (`.dts`/`.dtsi`) using Zephyr's pin control (`pinctrl`) bindings. See the `xiao_nrf54l15` board for a complete example.

## 5. Build and Flash

### Zephyr build

```bash
cd micropython-seeed-boards
export PROJECT_DIR=$(pwd)

# nRF54L15 example
west build ./lib/micropython/ports/zephyr --pristine \
  --board xiao_nrf54l15/nrf54l15/cpuapp --sysbuild -- \
  -DBOARD_ROOT=$PROJECT_DIR/ \
  -DEXTRA_DTC_OVERLAY_FILE=$PROJECT_DIR/boards/xiao_nrf54l15_nrf54l15_cpuapp.overlay \
  -DPM_STATIC_YML_FILE=$PROJECT_DIR/boards/pm_static_xiao_nrf54l15_nrf54l15_cpuapp.yml \
  -DEXTRA_CONF_FILE=$PROJECT_DIR/boards/xiao_nrf54l15_nrf54l15_cpuapp.conf

# MG24 example (uses upstream Zephyr board definition)
west build ./lib/micropython/ports/zephyr --pristine \
  --board xiao_mg24 -- \
  -DCONF_FILE=$PROJECT_DIR/boards/xiao_mg24.conf \
  -DEXTRA_DTC_OVERLAY_FILE=$PROJECT_DIR/boards/xiao_mg24.overlay
```

### Traditional build (Renesas RA, STM32, SAMD21)

```bash
cd micropython-seeed-boards

# Renesas RA
make -C lib/micropython/ports/renesas-ra BOARD_DIR=../../../../boards/seeed/xiao_ra4m1

# STM32 / SAMD21
make -C lib/micropython/ports/stm32 BOARD_DIR=../../../../boards/seeed/xiao_<board>
```

### Flash

Flash tools are provided in `tools/` per board. See the architecture reference for specific commands.

| Architecture | Method | Tool |
|---|---|---|
| nRF54L15 | nrfjprog / OpenOCD | `tools/xiao_nrf54l15_flash/` |
| MG24 | SLC CLI / J-Link | `tools/xiao_mg24_flash/` |
| RA4M1 | USB DFU / J-Link | `tools/xiao_ra4m1_flash/` |
| ESP32 | esptool | `esptool.py --port /dev/ttyUSB0 write_flash 0x0 firmware.bin` |
| RP2040 | UF2 drag-and-drop / picotool | `picotool load firmware.uf2` |
| SAMD21 | bossac / UF2 | `bossac -i -d -U true -i -e -w -v firmware.bin -R` |

## 6. Testing with pyboard

### Setup

```bash
pip install pyserial
export PATH=$PATH:micropython-seeed-boards/lib/micropython/tools
```

### Test script

```python
# test_xiao.py
import machine, time

def test_led():
    led = machine.Pin("LED", machine.Pin.OUT)
    for i in range(5):
        led.value(not led.value())
        time.sleep(0.5)
    print("PASS: LED toggle")

def test_gpio():
    pin = machine.Pin("D0", machine.Pin.IN, machine.Pin.PULL_UP)
    print(f"D0 state: {pin.value()}")
    print("PASS: GPIO input")

def test_i2c():
    i2c = machine.I2C(0)
    devices = i2c.scan()
    print(f"I2C devices: {[hex(d) for d in devices]}")
    print("PASS: I2C scan")

def test_adc():
    adc = machine.ADC(machine.Pin("D0"))
    print(f"ADC raw: {adc.read_u16()}")
    print("PASS: ADC read")

def test_pwm():
    pwm = machine.PWM(machine.Pin("LED"))
    pwm.freq(1000)
    for duty in range(0, 1024, 128):
        pwm.duty(duty)
        time.sleep(0.1)
    pwm.deinit()
    print("PASS: PWM output")

# Run all tests
tests = [test_led, test_gpio, test_i2c, test_adc, test_pwm]
passed = failed = 0
for t in tests:
    try:
        t()
        passed += 1
    except Exception as e:
        print(f"FAIL: {t.__name__} - {e}")
        failed += 1
print(f"\nResults: {passed} passed, {failed} failed")
```

### Execute

```bash
pyboard.py --device /dev/ttyACM0 test_xiao.py
```

## 7. Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `west build` fails: board not found | Missing `BOARD_ROOT` flag | Add `-DBOARD_ROOT=$PROJECT_DIR/` to west build command |
| `OSError: couldn't find board` | Board dir not found | Ensure `boards/seeed/xiao_<board>/` exists with correct files |
| Boot loop after flash | Wrong flash offset | Erase flash completely, check partition map in `.yml` |
| `pins.csv` parse error | Wrong format | Format is `logical_name,cpu_pin` with no header |
| USB not enumerated | Wrong VID/PID | Check `MICROPY_HW_USB_VID/PID` — must be real Seeed-assigned values |
| I2C scan returns nothing | Wrong SDA/SCL pins | Verify pins match schematic and MCU's I2C peripheral |
| Firmware too large | Too many frozen modules | Reduce `manifest.py` or adjust flash partition map |
| Zephyr Kconfig not applied | Missing `.conf` file | Add `-DEXTRA_CONF_FILE=...` or `-DCONF_FILE=...` to west build |
| Device tree overlay not applied | Missing overlay flag | Add `-DEXTRA_DTC_OVERLAY_FILE=...` to west build |
