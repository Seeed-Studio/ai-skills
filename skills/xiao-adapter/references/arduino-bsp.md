# Arduino BSP Adaptation for XIAO

## Table of Contents

1. [Base Repository Selection](#1-base-repository-selection)
2. [Directory Structure](#2-directory-structure)
3. [boards.txt Configuration](#3-boardstxt-configuration)
4. [Variant Files](#4-variant-files)
5. [pins_arduino.h Template](#5-pins_arduinoh-template)
6. [Compile and Upload](#6-compile-and-upload)
7. [Common Issues](#7-common-issues)

---

## 1. Base Repository Selection

Choose the BSP repo matching the target chip architecture:

| Architecture | Base Repository | Architecture Reference |
|---|---|---|
| SAMD21 / SAMD51 | `Seeed-Studio/ArduinoCore-samd` | [arch/samd21.md](arch/samd21.md) |
| ESP32 family | `espressif/arduino-esp32` | [arch/esp32.md](arch/esp32.md) |
| STM32 family | `stm32duino/Arduino_Core_STM32` | [arch/stm32.md](arch/stm32.md) |
| RP2040 | `arduino/arduino-pico` | [arch/rp2040.md](arch/rp2040.md) |
| nRF52 | `arduino/ArduinoCore-nRF528x-mbedos` | [arch/nrf52.md](arch/nrf52.md) |
| RISC-V | Vendor-specific core | Consult vendor docs |

> **Note**: For SAMD chips, always use Seeed's own fork `Seeed-Studio/ArduinoCore-samd` rather than the official Arduino repo. Seeed's fork includes XIAO-specific variant definitions and bootloader support.

Clone the base:

```bash
git clone https://github.com/<org>/<repo>.git
cd <repo>
git checkout <stable-tag>
```

If forking for Seeed:

```bash
git clone https://github.com/Seeed-Studio/<repo>.git
```

## 2. Directory Structure

After cloning, the XIAO variant should be placed under:

```
<Arduino_Core>/
├── boards.txt                    # Add board menu entries
├── platform.txt                  # Platform-level build config
├── variants/
│   └── seeed_xiao_<chip>/        # NEW: XIAO variant directory
│       ├── pins_arduino.h        # Pin definitions
│       ├── variant.h             # Board-specific macros
│       ├── variant.cpp           # Peripheral init (optional)
│       └── linker_script.ld      # Memory layout (if needed)
└── bootloaders/                  # If custom bootloader needed
```

## 3. boards.txt Configuration

Append board entries to `boards.txt`. Follow this template:

```
###############################################
## Seeed XIAO <Chip Name>
###############################################

seeed_xiao_<chip>.name=Seeed XIAO <Chip Name>
seeed_xiao_<chip>.build.mcu=<MCU_ID>
seeed_xiao_<chip>.build.f_cpu=<FREQUENCY>
seeed_xiao_<chip>.build.board=SEEED_XIAO_<CHIP>
seeed_xiao_<chip>.build.core=<CORE_NAME>
seeed_xiao_<chip>.build.variant=seeed_xiao_<chip>
seeed_xiao_<chip>.upload.tool=<UPLOAD_TOOL>
seeed_xiao_<chip>.upload.protocol=<PROTOCOL>
seeed_xiao_<chip>.upload.maximum_size=<FLASH_SIZE>
seeed_xiao_<chip>.upload.speed=<UPLOAD_SPEED>
seeed_xiao_<chip>.bootloader.tool=<BOOTLOADER_TOOL>
seeed_xiao_<chip>.bootloader.file=<BOOTLOADER_HEX>

# Menu options (optional but recommended)
seeed_xiao_<chip>.menu.opt.o2=Optimize for Size (-Os)
seeed_xiao_<chip>.menu.opt.o2.build.flags.optimize=-Os
seeed_xiao_<chip>.menu.opt.o3=Optimize for Speed (-O3)
seeed_xiao_<chip>.menu.opt.o3.build.flags.optimize=-O3

# Debug options
seeed_xiao_<chip>.menu.debug.on=Enabled
seeed_xiao_<chip>.menu.debug.on.build.flags.debug=-g
seeed_xiao_<chip>.menu.debug.off=Disabled
seeed_xiao_<chip>.menu.debug.off.build.flags.debug=
```

### Key Fields Explained

| Field | Description | Example |
|---|---|---|
| `build.mcu` | MCU identifier passed to compiler | `cortex-m4`, `esp32c3`, `rp2040` |
| `build.f_cpu` | CPU clock in Hz | `48000000L`, `160000000L` |
| `build.core` | Core variant to use | `arduino`, `stm32`, `esp32` |
| `build.variant` | Must match `variants/<name>/` | `seeed_xiao_<chip>` |
| `upload.tool` | Upload programmer tool | `openocd`, `esptool`, `picotool` |
| `upload.protocol` | Upload protocol | `swd`, `cmsis-dap`, `serial` |
| `upload.maximum_size` | Max sketch size in bytes | `262144`, `4194304` |

## 4. Variant Files

### variant.h

```cpp
#ifndef VARIANT_H
#define VARIANT_H

#include <stdint.h>
// Architecture-specific include goes here — see arch/<architecture>.md
// Examples: #include <WVariant.h> (SAMD), #include <Arduino.h> (most others)

// Board identifier
#define BOARD_NAME           "Seeed XIAO <Chip>"

// Clock
#define F_CPU               <CLOCK_FREQ>

// LED
#define LED_BUILTIN         <LED_PIN>
#define LED_GREEN           LED_BUILTIN

// Serial
#define SERIAL_PORT_USB     Serial
#define PIN_SERIAL_TX       <TX_PIN>
#define PIN_SERIAL_RX       <RX_PIN>

// SPI
#define PIN_SPI_SS          <SS_PIN>
#define PIN_SPI_MOSI        <MOSI_PIN>
#define PIN_SPI_MISO        <MISO_PIN>
#define PIN_SPI_SCK         <SCK_PIN>

// Wire (I2C)
#define PIN_WIRE_SDA        <SDA_PIN>
#define PIN_WIRE_SCL        <SCL_PIN>

// ADC
#define ADC_RESOLUTION      <BITS>
#define PIN_A0              <A0_PIN>
#define PIN_A1              <A1_PIN>
#define PIN_A2              <A2_PIN>
#define PIN_A3              <A3_PIN>

#endif
```

### variant.cpp (if needed)

Some architectures require a `variant.cpp` with peripheral pin mapping (e.g., `PinDescription` arrays). See the architecture-specific reference for details:

- SAMD21: `PinDescription` array required — see [arch/samd21.md](arch/samd21.md)
- ESP32: GPIO matrix, no PinDescription needed — see [arch/esp32.md](arch/esp32.md)
- STM32: `PinMap` in core, no PinDescription — see [arch/stm32.md](arch/stm32.md)

## 5. pins_arduino.h Template

This is the core pin mapping file. Map physical pins to Arduino digital/analog pin numbers:

```cpp
#ifndef PINS_ARDUINO_H
#define PINS_ARDUINO_H

#include <Arduino.h>

// Digital pin mapping
// Each XIAO exposes 11 usable GPIO (D0-D10) via castellated pads
static const uint8_t D0   = <PIN_D0>;   // Also A0 / UART RX
static const uint8_t D1   = <PIN_D1>;   // Also A1 / UART TX
static const uint8_t D2   = <PIN_D2>;   // Also A2 / SPI CS
static const uint8_t D3   = <PIN_D3>;   // Also A3
static const uint8_t D4   = <PIN_D4>;   // I2C SDA
static const uint8_t D5   = <PIN_D5>;   // I2C SCL
static const uint8_t D6   = <PIN_D6>;
static const uint8_t D7   = <PIN_D7>;
static const uint8_t D8   = <PIN_D8>;   // SPI SCK
static const uint8_t D9   = <PIN_D9>;   // SPI MISO
static const uint8_t D10  = <PIN_D10>;  // SPI MOSI
static const uint8_t LED_BUILTIN = <LED_PIN>;

// Analog pin mapping (aliases into digital pins)
#define PIN_A0   D0
#define PIN_A1   D1
#define PIN_A2   D2
#define PIN_A3   D3
static const uint8_t A0 = PIN_A0;
static const uint8_t A1 = PIN_A1;
static const uint8_t A2 = PIN_A2;
static const uint8_t A3 = PIN_A3;

// Total digital pin count
#define NUM_DIGITAL_PINS    14  // D0-D10 + internal pins
#define NUM_ANALOG_INPUTS   4

// PWM-capable pins (update based on MCU timer channels — see arch/<architecture>.md)
#define PWM_PIN_LIST        { D0, D1, D2, D3, D5, D6, D9, D10 }

// Interrupt-capable pins
#define INTERRUPT_PIN_LIST  { D0, D1, D2, D3, D4, D5, D6, D7 }

#endif
```

### Pin Mapping Rules

1. **Consult the schematic** — the XIAO PCB routes specific MCU pins to specific castellated pads
2. **Reserve LED pin** — typically active LOW on XIAO boards
3. **Check pin mux** — ensure peripheral pins (SPI/I2C/UART) use the MCU's hardware peripheral pins, not GPIO bit-bang
4. **ADC channels** — only assign analog pins to pins with actual ADC capability on the MCU
5. **PWM channels** — only assign PWM to pins connected to hardware timer outputs (see architecture reference)

## 6. Compile and Upload

### Install arduino-cli

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

### Install core with local path

```bash
arduino-cli config add board_manager.additional_urls https://raw.githubusercontent.com/<org>/<repo>/master/package_<vendor>_index.json
arduino-cli core update-index
arduino-cli core install <vendor>:<arch>
```

For local development (point to cloned repo):

```bash
# Create a local hardware folder
mkdir -p ~/Arduino/hardware/<vendor>/<arch>
# Symlink or copy the cloned core
ln -s /path/to/cloned/core/* ~/Arduino/hardware/<vendor>/<arch>/
```

### Compile

```bash
arduino-cli compile \
  --fqbn <vendor>:<arch>:seeed_xiao_<chip> \
  --build-path ./build \
  ./test_sketch
```

### Upload

```bash
arduino-cli upload \
  --fqbn <vendor>:<arch>:seeed_xiao_<chip> \
  --port <PORT> \
  --verify \
  ./test_sketch
```

### Test Sketches

**Blink:**
```cpp
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}
void loop() {
  digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  delay(1000);
}
```

**Serial Echo:**
```cpp
void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("XIAO Serial Echo Test");
}
void loop() {
  if (Serial.available()) {
    Serial.write(Serial.read());
  }
}
```

**I2C Scanner:**
```cpp
#include <Wire.h>
void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("I2C Scanner");
}
void loop() {
  byte error, address;
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Found at 0x");
      Serial.println(address, HEX);
    }
  }
  delay(5000);
}
```

## 7. Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `variant.h not found` | `build.variant` path mismatch | Ensure `variants/seeed_xiao_<chip>/` exists and name matches `boards.txt` |
| Upload timeout | Wrong upload speed or protocol | Check `upload.speed` and `upload.protocol` match the debug probe |
| Blink wrong speed | `build.f_cpu` mismatch | Verify F_CPU matches actual clock config in `variant.cpp` |
| SPI not working | Pin mux conflict | Ensure SPI pins in `pins_arduino.h` match MCU hardware SPI pins |
| Serial not working | USB CDC not configured | For USB-capable MCUs, enable CDC in core config; for UART, check TX/RX pins |
| Compilation error in variant.cpp | Architecture-specific include or type missing | Read the [architecture reference](arch/) for required includes and types |
