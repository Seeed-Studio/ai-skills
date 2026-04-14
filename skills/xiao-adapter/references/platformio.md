# PlatformIO Adaptation for XIAO

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [platformio.ini Configuration](#2-platformioini-configuration)
3. [Board JSON Definition](#3-board-json-definition)
4. [Adding Board to Seeed Platform](#4-adding-board-to-seeed-platform)
5. [Compile and Upload](#5-compile-and-upload)
6. [Test Projects](#6-test-projects)
7. [Common Issues](#7-common-issues)

---

## 1. Platform Overview

Seeed maintains a **unified PlatformIO platform** that hosts all XIAO board definitions:

- **Repository**: `https://github.com/Seeed-Studio/platform-seeedboards`
- **Platform name**: `Seeed Studio`
- **Board ID format**: `seeed-xiao-<chip>` (hyphens, NOT underscores)

The platform auto-detects the MCU architecture from the board ID and routes to architecture-specific builder scripts:

| Board ID pattern | Architecture | Builder script | Framework package |
|---|---|---|---|
| `*esp32*` | ESP32 | `builder/board_build/esp/` | `framework-arduinoespressif32` |
| `*samd*` | SAMD21/SAMD51 | `builder/board_build/samd/` | `framework-arduino-samd-seeed` |
| `*rp2040*` / `*rp2350*` | RP2040/RP2350 | `builder/board_build/rpi/` | `framework-arduinopico` |
| `*nrf*` / `*52840*` | nRF52/nRF54 | `builder/board_build/nrf/` | `framework-arduinoadafruitnrf52` |
| `*ra4m1*` | Renesas RA4M1 | `builder/board_build/renesas/` | `framework-arduinorenesas-uno` |
| `*mg24*` | Silicon Labs MG24 | `builder/board_build/siliconlab/` | `framework-arduino-silabs` |

> **Important**: Board IDs must match the detection keywords above. For example, a SAMD21 board ID must contain `"samd"`.

### Installation

```bash
# Stable (from PlatformIO registry)
pio platform install "Seeed Studio"

# Development (from GitHub)
pio platform install "https://github.com/Seeed-Studio/platform-seeedboards.git"
```

## 2. platformio.ini Configuration

### Standard project structure

```
xiao-<chip>-test/
├── platformio.ini
├── boards/
│   └── seeed-xiao-<chip>.json   # Custom board definition (if not in platform)
├── src/
│   └── main.cpp
└── lib/
    └── README
```

### Basic platformio.ini template

```ini
; Seeed XIAO <Chip Name> PlatformIO Configuration
[platformio]
default_envs = seeed-xiao-<chip>

[env]
monitor_speed = 115200

[env:seeed-xiao-<chip>]
platform = Seeed Studio
board = seeed-xiao-<chip>
framework = arduino
```

### Using local variant (development)

When developing a new variant that hasn't been merged into the platform's framework yet, use `board_build.variants_dir` to point to a project-local variant directory:

```ini
[env:seeed-xiao-samd21plus]
platform = Seeed Studio
board = seeed-xiao-samd21plus
framework = arduino

; Use project-local variant directory (instead of framework's built-in variants/)
board_build.variants_dir = variants

upload_protocol = sam-ba
```

Project structure with local variant:

```
xiao-samd21plus-test/
├── platformio.ini
├── boards/
│   └── seeed-xiao-samd21plus.json
├── variants/
│   └── seeed_xiao_samd21plus/    # must match build.variant in board JSON
│       ├── variant.h
│       ├── variant.cpp
│       ├── pins_arduino.h
│       └── linker_scripts/
└── src/
    └── main.cpp
```

> **Note**: The variant directory name under `variants/` must match the `build.variant` field in the board JSON exactly.

### Multi-environment configuration

```ini
[platformio]
default_envs = seeed-xiao-<chip>

[env]
monitor_speed = 115200

[env:seeed-xiao-<chip>_arduino]
platform = Seeed Studio
board = seeed-xiao-<chip>
framework = arduino

[env:seeed-xiao-<chip>_zephyr]
platform = Seeed Studio
board = seeed-xiao-<chip>
framework = zephyr
```

## 3. Board JSON Definition

Board JSON files follow architecture-specific formats. **Always** read the architecture reference before creating a board JSON — each architecture has required fields that differ from the generic template.

### Architecture-specific references

| Architecture | Reference | Key differences |
|---|---|---|
| SAMD21/SAMD51 | [arch/samd21.md — PlatformIO Board JSON](arch/samd21.md#platformio-board-json-seeed-unified-platform) | `core: "seeed"`, `system: "samd"`, `arduino.ldscript`, `openocd_chipname` |
| ESP32 | [arch/esp32.md](arch/esp32.md) | `core: "esp32"`, partition table, flash mode |
| RP2040/RP2350 | [arch/rp2040.md](arch/rp2040.md) | `core: "earlephilhower"`, boot2 source |
| nRF52/nRF52840 | [arch/nrf52.md](arch/nrf52.md) | `core: "nRF5"`, softdevice, BSP name |
| STM32 | [arch/stm32.md](arch/stm32.md) | `core` varies by framework |
| nRF54L15 | [arch/nrf52.md](arch/nrf52.md) | Uses Zephyr framework |

### Board JSON naming and ID convention

- **Filename**: `seeed-xiao-<chip>.json` (hyphens)
- **Board ID**: matches filename without `.json` extension
- **Reference in platformio.ini**: `board = seeed-xiao-<chip>`

### Generic board JSON structure

```json
{
  "build": {
    "core": "<see platform table above>",
    "cpu": "<cpu_arch>",
    "extra_flags": ["<arch-specific flags>"],
    "f_cpu": "<clock_freq>",
    "hwids": [["<VID>", "<PID>"], ["<VID>", "<bootloader_PID>"]],
    "mcu": "<mcu_part_number>",
    "usb_product": "Seeed XIAO <Chip Name>",
    "variant": "<variant_dir_name>"
  },
  "debug": {
    "jlink_device": "<jlink_device>",
    "openocd_target": "<openocd_target>",
    "svd_path": "<path_to_svd_file>"
  },
  "frameworks": ["arduino"],
  "name": "Seeed XIAO <Chip Name>",
  "upload": {
    "maximum_ram_size": <ram_bytes>,
    "maximum_size": <flash_bytes>,
    "protocol": "<upload_protocol>",
    "protocols": ["<protocol1>", "<protocol2>"]
  },
  "url": "https://wiki.seeedstudio.com/XIAO_<CHIP>/",
  "vendor": "Seeed Studio"
}
```

> **Important**: This generic template is a starting point only. Each architecture adds required fields — see the architecture reference links above.

## 4. Adding Board to Seeed Platform

New XIAO boards should be added to the `Seeed-Studio/platform-seeedboards` repository:

### Step 1: Create board JSON

Create `boards/seeed-xiao-<chip>.json` following the architecture-specific format.

### Step 2: Add to platform (if needed)

If the architecture is new or requires new packages, update:

1. **`platform.json`** — add framework/toolchain packages if not already present
2. **`platform_cfg/<arch>_cfg.py`** — add architecture-specific package configuration
3. **`builder/board_build/<arch>/`** — add or update build scripts
4. **`builder/frameworks/arduino.py`** — add routing for the new board ID pattern

### Step 3: Add framework package to platform.json

For SAMD boards, the framework is already configured. For new architectures, add to `platform.json` `packages`:

```json
"framework-arduino-<vendor>": {
  "type": "framework",
  "optional": true,
  "owner": "<owner>",
  "version": "<source_url_or_version>"
}
```

### Step 4: Submit PR to platform-seeedboards

```bash
cd platform-seeedboards
git checkout -b add-seeed-xiao-<chip>
# Add board JSON and any platform changes
git add boards/seeed-xiao-<chip>.json
git commit -m "feat: add Seeed XIAO <Chip Name> board support"
git push origin add-seeed-xiao-<chip>
# Create PR on GitHub
```

## 5. Compile and Upload

### Compile

```bash
pio run -e seeed-xiao-<chip>
```

### Upload

```bash
pio run -e seeed-xiao-<chip> --target upload
```

### Upload with specific port

```bash
pio run -e seeed-xiao-<chip> --target upload --upload-port /dev/ttyUSB0
```

### Clean build

```bash
pio run -e seeed-xiao-<chip> --target clean
```

### Serial monitor

```bash
pio device monitor -e seeed-xiao-<chip>
```

### Compile + upload + monitor

```bash
pio run -e seeed-xiao-<chip> --target upload && pio device monitor
```

## 6. Test Projects

### Blink test (src/main.cpp)

```cpp
#include <Arduino.h>

#ifndef LED_BUILTIN
#define LED_BUILTIN <LED_PIN>
#endif

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  delay(1000);
}
```

### GPIO + Serial test

```cpp
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  pinMode(D0, INPUT_PULLUP);
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.println("XIAO PlatformIO GPIO Test");
}

void loop() {
  int state = digitalRead(D0);
  Serial.print("D0 state: ");
  Serial.println(state);
  digitalWrite(LED_BUILTIN, !state);
  delay(500);
}
```

### I2C Scanner

```cpp
#include <Arduino.h>
#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.println("I2C Scanner");
}

void loop() {
  byte error, address;
  int deviceCount = 0;
  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();
    if (error == 0) {
      Serial.print("Found device at 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
      deviceCount++;
    }
  }
  if (deviceCount == 0) Serial.println("No I2C devices found");
  delay(5000);
}
```

## 7. Common Issues

| Problem | Cause | Solution |
|---|---|---|
| `Unknown board` | Board JSON not found | Check JSON filename matches `platformio.ini` board value |
| `Platform not found` | Seeed platform not installed | Run `pio platform install "Seeed Studio"` |
| Build error: undefined `LED_BUILTIN` | Missing variant or macro | Add `build_flags = -DLED_BUILTIN=<pin>` to `platformio.ini` |
| Upload failed: no access | Linux USB permissions | Add user to `dialout` group or use `sudo` |
| Linker error: RAM overflow | Too large for MCU RAM | Optimize code or select a larger RAM variant |
| Wrong flash size | `maximum_size` mismatch | Verify against MCU datasheet and adjust board JSON |
| `AssertionError` (SAMD) | Missing `openocd_chipname` in board JSON | Add `debug.openocd_chipname` — see [arch/samd21.md](arch/samd21.md#required-debug-fields) |
| `Missed J-Link Device ID` (SAMD) | Missing `jlink_device` in board JSON | Add `debug.jlink_device` — see [arch/samd21.md](arch/samd21.md#required-debug-fields) |
| `USB_VID`/`USB_PID` not declared | Missing or wrong `build.hwids` | Use `build.hwids` array format — see [arch/samd21.md](arch/samd21.md#required-build-fields) |
| Board not detected by platform | Board ID doesn't match detection keyword | Board ID must contain architecture keyword (`samd`, `esp32`, `nrf`, etc.) |
| Wrong framework package | Used official package name | Use Seeed's package name (e.g., `framework-arduino-samd-seeed`, NOT `framework-arduino-samd`) |
