# MicroPython Porting for XIAO

## Table of Contents

1. [Port Selection](#1-port-selection)
2. [Directory Structure](#2-directory-structure)
3. [Core Configuration Files](#3-core-configuration-files)
4. [Pin Definition](#4-pin-definition)
5. [Board Initialization](#5-board-initialization)
6. [Build Configuration](#6-build-configuration)
7. [Compile and Flash](#7-compile-and-flash)
8. [Automated Testing with pyboard](#8-automated-testing-with-pyboard)
9. [Common Issues](#9-common-issues)

---

## 1. Port Selection

Choose the closest existing port in `micropython/ports/` as the base:

| Architecture | Port Directory | Suitable For |
|---|---|---|
| ARM Cortex-M | `ports/stm32/` | STM32, GD32, ATSAM |
| ARM Cortex-M (bare) | `ports/nrf/` | Nordic nRF52 |
| ESP32 Xtensa | `ports/esp32/` | ESP32, ESP32-S2/S3/C3/C6 |
| RP2040 ARM | `ports/rp2/` | RP2040 |
| RISC-V | `ports/rp2/` (multi-arch) | RISC-V MCUs with RP2-like structure |
| MIPS | `ports/pic16bit/` | PIC (rarely used for XIAO) |

Clone MicroPython:

```bash
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init --recursive
```

## 2. Directory Structure

Board-specific files to create/modify:

```
micropython/
├── ports/<port>/
│   ├── boards/
│   │   └── SEEED_XIAO_<CHIP>/         # NEW: Board directory
│   │       ├── board.json              # Board descriptor
│   │       ├── manifest.py             # Freeze modules list
│   │       ├── mpconfigboard.h         # Board-level config
│   │       ├── mpconfigboard.mk        # Build variables
│   │       ├── pins.csv                # Pin mapping table
│   │       └── board_init.c            # Board init code (if needed)
│   ├── mpconfigport.h                  # Port-level defaults
│   └── Makefile                        # Build system
```

## 3. Core Configuration Files

### mpconfigboard.h

Board-level MicroPython configuration:

```c
// Seeed XIAO <Chip Name> board configuration
#define MICROPY_HW_BOARD_NAME       "Seeed XIAO <Chip>"
#define MICROPY_HW_MCU_NAME         "<MCU_NAME>"
#define MICROPY_HW_FLASH_FS_LABEL   "XIAO"

// Flash and RAM configuration
#define MICROPY_HW_FLASH_STORAGE_SIZE      (FLASH_SIZE - 0x4000)  // Reserve space
#define MICROPY_HW_FLASH_STORAGE_BASE      0x08000000             // Adjust per MCU
#define MICROPY_HW_FLASH_STORAGE_ALIGNMENT  512

// UART configuration
#define MICROPY_HW_UART0_TX        <TX_PIN>
#define MICROPY_HW_UART0_RX        <RX_PIN>
#define MICROPY_HW_UART0_BAUDRATE  115200

// I2C configuration
#define MICROPY_HW_I2C0_SCL        <SCL_PIN>
#define MICROPY_HW_I2C0_SDA        <SDA_PIN>

// SPI configuration
#define MICROPY_HW_SPI0_SCK        <SCK_PIN>
#define MICROPY_HW_SPI0_MOSI       <MOSI_PIN>
#define MICROPY_HW_SPI0_MISO       <MISO_PIN>

// LED
#define MICROPY_HW_LED1            <LED_PIN>           // Active LOW on XIAO
#define MICROPY_HW_LED_PULLUP      1                   // Enable pull-up

// USB configuration (if USB-capable MCU)
// IMPORTANT: VID/PID must be applied from Seeed internal team, never fabricate values
// Ask user to contact the responsible internal team for official VID/PID assignment
#define MICROPY_HW_USB_VID         <USER_PROVIDED_VID> // e.g. 0x2886 (Seeed VID)
#define MICROPY_HW_USB_PID         <USER_PROVIDED_PID> // Unique PID per board variant
#define MICROPY_HW_USB_CDC         (1)                 // Enable USB CDC

// Enable/disable features
#define MICROPY_HW_ENABLE_UART     (1)
#define MICROPY_HW_ENABLE_SPI      (1)
#define MICROPY_HW_ENABLE_I2C      (1)
#define MICROPY_HW_ENABLE_ADC      (1)
#define MICROPY_HW_ENABLE_DAC      (0)                 // If no DAC on MCU
#define MICROPY_HW_ENABLE_CAN      (0)                 // If no CAN on MCU
#define MICROPY_HW_ENABLE_USB      (1)                 // If USB on MCU
```

### mpconfigboard.mk

Build variables for the board:

```makefile
# Seeed XIAO <Chip> build configuration
MCU_SERIES = <mcu_series>
CMSIS_MCU = <cmsis_mcu>
AF_FILE = boards/<mcu_series>_af.csv
LD_FILES = boards/<mcu_series>_ld.ld

# MicroPython feature flags
MICROPY_PY_BLUETOOTH = 0
MICROPY_PY_NETWORK = 0
MICROPY_PY_USOCKET = 0
MICROPY_PY_WEBREPL = 1
MICROPY_PY_UJSON = 1
MICROPY_PY_URE = 1
MICROPY_PY_UHEAPQ = 1
MICROPY_PY_UTIMEQ = 1
MICROPY_PY_UHASHLIB = 1
MICROPY_PY_UCRYPTOLIB = 0
MICROPY_PY_UCTYPES = 1
MICROPY_PY_UZLIB = 1
MICROPY_PY_UASYNCIO = 1
MICROPY_PY_FRAMEBUF = 1
MICROPY_VFS_FAT = 1

# Freeze modules (files to embed in firmware)
FROZEN_MANIFEST = $(BOARD_DIR)/manifest.py
```

### manifest.py

Define which Python modules to freeze into firmware:

```python
# manifest.py for Seeed XIAO <Chip>

freeze("$(PORT_DIR)/modules")
```

## 4. Pin Definition

### pins.csv Format

```
# XIAO <Chip> pin mapping
# Format: board_pin, pin_name, pin_function
D0, PA10, GPIO
D1, PA9, GPIO
D2, PA0, GPIO
D3, PA1, GPIO
D4, PB7, GPIO
D5, PB6, GPIO
D6, PA7, GPIO
D7, PA6, GPIO
D8, PA5, GPIO
D9, PA4, GPIO
D10, PA3, GPIO
D11, PA2, GPIO
LED, PB1, GPIO
```

### Pin naming conventions for MicroPython

- **board_pin**: The name exposed to MicroPython users (e.g., `D0`, `LED`)
- **pin_name**: The MCU port/pin (e.g., `PA10`, `PB6`, `GPIO0`)
- **pin_function**: Always `GPIO` for basic pins; some ports support `ALT` for alternate functions

### STM32-specific pin CSV

```
D0, PA10, GPIO
D1, PA9, GPIO
D2, PA0, GPIO
D3, PA1, GPIO
D4, PB7, GPIO
D5, PB6, GPIO
D6, PA7, GPIO
D7, PA6, GPIO
D8, PA5, GPIO
D9, PA4, GPIO
D10, PA3, GPIO
LED, PB1, GPIO
```

### ESP32-specific pin CSV

```
D0, GPIO0, GPIO
D1, GPIO1, GPIO
D2, GPIO2, GPIO
D3, GPIO3, GPIO
D4, GPIO4, GPIO
D5, GPIO5, GPIO
D6, GPIO6, GPIO
D7, GPIO7, GPIO
D8, GPIO8, GPIO
D9, GPIO9, GPIO
D10, GPIO10, GPIO
LED, GPIO11, GPIO
```

### RP2-specific pin CSV

```
D0, GPIO0, GPIO
D1, GPIO1, GPIO
D2, GPIO2, GPIO
D3, GPIO3, GPIO
D4, GPIO4, GPIO
D5, GPIO5, GPIO
D6, GPIO6, GPIO
D7, GPIO7, GPIO
D8, GPIO8, GPIO
D9, GPIO9, GPIO
D10, GPIO10, GPIO
LED, GPIO11, GPIO
```

## 5. Board Initialization

### board_init.c

Custom board initialization (optional, only if non-default init is needed):

```c
#include <stdint.h>
#include "py/mphal.h"
#include "board_init.h"

// Called early in startup, before Python runtime
void board_early_init(void) {
    // Example: configure external oscillator
    // Example: set up debug UART pins
    // Example: configure USB D+ pull-up
}

// Called after Python runtime is initialized
void board_init(void) {
    // Example: initialize onboard sensors
    // Example: configure RGB LED controller
    // Example: set up power management IC
}

// Called before entering low-power mode
void board_sleep_prepare(void) {
    // Example: turn off unnecessary peripherals
    // Example: configure wake-up sources
}
```

### board.json (for newer MicroPython versions)

```json
{
  "build": {
    "board_name": "SEEED_XIAO_<CHIP>",
    "mcu": "<MCU_NAME>",
    "f_cpu": "<CLOCK_FREQ>",
    "ram_size": <RAM_BYTES>,
    "flash_size": <FLASH_BYTES>
  },
  "id": "seeed_xiao_<chip>",
  "name": "Seeed XIAO <Chip Name>",
  "vendor": "Seeed Studio",
  "url": "https://wiki.seeedstudio.com/XIAO_<CHIP>/",
  "usb_pid": "<USER_PROVIDED_PID>"  // Must apply from Seeed internal team
}
```

## 6. Build Configuration

### Prerequisites

```bash
# Install required tools (Debian/Ubuntu)
sudo apt install build-essential gcc-arm-none-eabi libnewlib-arm-none-eabi \
                 python3 python3-pip git wget

# For ESP32 port
sudo apt install python3-venv ccache

# For RP2 port
sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi
```

### Cross-compiler setup (STM32 example)

```bash
# ARM GCC toolchain
sudo apt install gcc-arm-none-eabi

# Verify
arm-none-eabi-gcc --version
```

### Build steps (STM32)

```bash
cd micropython/ports/stm32

# Submodule update (first time)
make submodules

# Build for XIAO board
make BOARD=SEEED_XIAO_<CHIP>

# Build with cross-compiler
make BOARD=SEEED_XIAO_<CHIP> CROSS_COMPILE=arm-none-eabi-
```

### Build steps (ESP32)

```bash
cd micropython/ports/esp32

# Setup ESP-IDF (first time)
make submodules
cd esp-idf && ./install.sh && cd ..

# Build for XIAO board
make BOARD=SEEED_XIAO_<CHIP>
```

### Build steps (RP2)

```bash
cd micropython/ports/rp2

# Submodule update (first time)
make submodules

# Build for XIAO board
make BOARD=SEEED_XIAO_<CHIP>
```

## 7. Compile and Flash

### Build firmware

```bash
cd micropython/ports/<port>
make BOARD=SEEED_XIAO_<CHIP>
```

Output firmware files are typically in `build-SEEED_XIAO_<CHIP>/`:
- `firmware.hex` — Intel HEX format
- `firmware.bin` — Raw binary
- `firmware.uf2` — UF2 format (RP2040)

### Flash via OpenOCD (STM32)

```bash
# Via CMSIS-DAP
openocd -f interface/cmsis-dap.cfg -f target/stm32f1x.cfg \
        -c "program build-SEEED_XIAO_<CHIP>/firmware.hex verify reset exit"

# Via ST-Link
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg \
        -c "program build-SEEED_XIAO_<CHIP>/firmware.hex verify reset exit"
```

### Flash via esptool (ESP32)

```bash
esptool.py --chip esp32c3 --port /dev/ttyUSB0 --baud 460800 \
           write_flash -z 0x0 build-SEEED_XIAO_<CHIP>/firmware.bin
```

### Flash via picotool (RP2040)

```bash
# Hold BOOTSEL, connect USB, release
picotool load build-SEEED_XIAO_<CHIP>/firmware.uf2

# Or copy .uf2 to mass storage
cp build-SEEED_XIAO_<CHIP>/firmware.uf2 /media/<user>/RPI-RP2/
```

### Flash via STM32CubeProgrammer (STM32, GUI)

1. Connect debugger (ST-Link / CMSIS-DAP)
2. Select `firmware.hex` file
3. Click "Download"

## 8. Automated Testing with pyboard

### Setup pyboard.py

```bash
pip install pyserial
# pyboard.py is in micropython/tools/
export PATH=$PATH:/path/to/micropython/tools
```

### Run test script remotely

Create `test_xiao.py`:

```python
# test_xiao.py - Automated hardware test for XIAO
import machine, time, sys

def test_led():
    """Test onboard LED toggle"""
    led = machine.Pin("LED", machine.Pin.OUT)
    for i in range(5):
        led.value(not led.value())
        time.sleep(0.5)
    print("PASS: LED toggle")

def test_uart():
    """Test UART echo"""
    uart = machine.UART(0, baudrate=115200)
    uart.write("XIAO UART Test\n")
    print("PASS: UART TX")

def test_gpio():
    """Test GPIO input with pull-up"""
    pin = machine.Pin("D0", machine.Pin.IN, machine.Pin.PULL_UP)
    val = pin.value()
    print(f"D0 state: {val}")
    print("PASS: GPIO input")

def test_i2c():
    """Test I2C bus scan"""
    i2c = machine.I2C(0)
    devices = i2c.scan()
    print(f"I2C devices found: {[hex(d) for d in devices]}")
    print("PASS: I2C scan")

def test_spi():
    """Test SPI loopback"""
    spi = machine.SPI(0, mode=0)
    spi.init(baudrate=1000000)
    result = spi.write_readbytes(b"\xAB\xCD", 2)
    print(f"SPI loopback: {result}")
    print("PASS: SPI loopback")

def test_adc():
    """Test ADC reading"""
    adc = machine.ADC(machine.Pin("D0"))
    val = adc.read_u16()
    print(f"ADC D0 raw: {val}")
    print("PASS: ADC read")

def test_pwm():
    """Test PWM output"""
    pwm = machine.PWM(machine.Pin("LED"))
    pwm.freq(1000)
    for duty in range(0, 1024, 128):
        pwm.duty(duty)
        time.sleep(0.1)
    pwm.deinit()
    print("PASS: PWM output")

# Run all tests
tests = [test_led, test_uart, test_gpio, test_i2c, test_spi, test_adc, test_pwm]
passed = 0
failed = 0
for t in tests:
    try:
        t()
        passed += 1
    except Exception as e:
        print(f"FAIL: {t.__name__} - {e}")
        failed += 1

print(f"\nResults: {passed} passed, {failed} failed")
```

### Execute via pyboard.py

```bash
# Run test script on connected board
pyboard.py --device /dev/ttyACM0 test_xiao.py

# Run interactive commands
pyboard.py --device /dev/ttyACM0 -c "import machine; print(machine.Pin('LED', machine.Pin.OUT))"

# Enter REPL
pyboard.py --device /dev/ttyACM0 -c "import micropython; micropython.kbd_intr(); import repl; repl.enter()"
```

## 9. Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `OSError: couldn't find board` | Board dir not found | Ensure `boards/SEEED_XIAO_<CHIP>/` exists with correct `mpconfigboard.mk` |
| Boot loop after flash | Wrong flash offset or corrupt firmware | Erase flash completely, check flash base address |
| `pins.csv` parse error | Wrong pin format | Ensure format is `board_pin, pin_name, pin_function` with no trailing spaces |
| USB not enumerated | Wrong VID/PID or USB not configured | Check `MICROPY_HW_USB_VID/PID` and USB pin config |
| I2C scan returns nothing | Wrong SDA/SCL pins | Verify pins match schematic and MCU's I2C peripheral pins |
| Firmware too large | Exceeded flash with frozen modules | Reduce `FROZEN_MANIFEST` or increase `MICROPY_HW_FLASH_STORAGE_SIZE` |
| `ImportError: no module` | Feature not enabled | Enable in `mpconfigboard.mk` (e.g., `MICROPY_PY_UJSON = 1`) |
