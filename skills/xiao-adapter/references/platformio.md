# PlatformIO Adaptation for XIAO

## Table of Contents

1. [Platform Selection](#1-platform-selection)
2. [platformio.ini Configuration](#2-platformioini-configuration)
3. [Custom Board Definition](#3-custom-board-definition)
4. [Custom Platform Creation](#4-custom-platform-creation)
5. [Compile and Upload](#5-compile-and-upload)
6. [Test Projects](#6-test-projects)
7. [Common Issues](#7-common-issues)

---

## 1. Platform Selection

Check if the target MCU is already supported by an existing PlatformIO platform:

| MCU Vendor | Platform | Install Command | Architecture Reference |
|---|---|---|---|
| ST STM32 | `ststm32` | `pio pkg install -p "platformio/ststm32"` | [arch/stm32.md](arch/stm32.md) |
| Espressif ESP32 | `espressif32` | `pio pkg install -p "platformio/espressif32"` | [arch/esp32.md](arch/esp32.md) |
| Raspberry Pi RP2040 | `raspberrypi` | `pio pkg install -p "platformio/raspberrypi"` | [arch/rp2040.md](arch/rp2040.md) |
| Microchip SAMD | `atmelsam` | `pio pkg install -p "platformio/atmelsam"` | [arch/samd21.md](arch/samd21.md) |
| Nordic nRF52 | `nordicnrf52` | `pio pkg install -p "platformio/nordicnrf52"` | [arch/nrf52.md](arch/nrf52.md) |
| GigaDevice GD32 | `gd32` | Check vendor registry | [arch/stm32.md](arch/stm32.md) |
| Bouffalo Lab BL | Vendor-specific | Check vendor registry | Consult vendor docs |

If no official platform exists, proceed to [Custom Platform Creation](#4-custom-platform-creation).

## 2. platformio.ini Configuration

### Standard project structure

```
xiao-<chip>-test/
├── platformio.ini
├── include/
│   └── README
├── src/
│   └── main.cpp
└── lib/
    └── README
```

### Basic platformio.ini template

```ini
; Seeed XIAO <Chip Name> PlatformIO Configuration
[env:seeed_xiao_<chip>]
platform = <platform_name>
board = seeed_xiao_<chip>
framework = arduino

; Build options
build_flags =
  -DARDUINO_SEEED_XIAO_<CHIP>
  -DUSBCON

; Upload options
upload_protocol = <protocol>
upload_speed = <speed>

; Monitor
monitor_speed = 115200
monitor_filters = direct
```

> **Note**: For chip-specific build flags (e.g., STM32 HSE_VALUE, ESP32 partition table), see the [architecture reference](arch/).

### Multi-environment configuration

```ini
[platformio]
default_envs = seeed_xiao_<chip>

; Common settings
[env]
monitor_speed = 115200

; XIAO <Chip> - Arduino framework
[env:seeed_xiao_<chip>_arduino]
platform = <platform_name>
board = seeed_xiao_<chip>
framework = arduino
build_flags = -DARDUINO_SEEED_XIAO_<CHIP>

; XIAO <Chip> - bare metal (if supported)
[env:seeed_xiao_<chip>_bare]
platform = <platform_name>
board = seeed_xiao_<chip>
framework = zephyr  ; or mbed, etc.
build_flags = -DBOARD_SEEED_XIAO_<CHIP>
```

## 3. Custom Board Definition

If the board is not in the official platform, create a custom board definition.

### Board JSON file

Create `boards/seeed_xiao_<chip>.json`:

```json
{
  "build": {
    "core": "<core_name>",
    "cpu": "<cpu_arch>",
    "f_cpu": "<clock_freq>",
    "mcu": "<mcu_part_number>",
    "variant": "seeed_xiao_<chip>"
  },
  "connectivity": [
    "uart",
    "spi",
    "i2c",
    "usb"
  ],
  "debug": {
    "default_tools": [
      "<debug_tool>"
    ],
    "jlink_device": "<jlink_device>",
    "openocd_target": "<openocd_target>",
    "svd_path": "<path_to_svd_file>"
  },
  "frameworks": [
    "arduino",
    "zephyr"
  ],
  "name": "Seeed XIAO <Chip Name>",
  "upload": {
    "maximum_ram_size": <ram_bytes>,
    "maximum_size": <flash_bytes>,
    "protocol": "<upload_protocol>",
    "protocols": [
      "<protocol1>",
      "<protocol2>"
    ]
  },
  "url": "https://wiki.seeedstudio.com/XIAO_<CHIP>/",
  "vendor": "Seeed Studio"
}
```

> **Important**: Many platforms have **required** board JSON fields that differ from this generic template. **Always** check the architecture reference before generating the board JSON:
>
> - **atmelsam** (SAMD21/SAMD51): Requires `debug.openocd_chipname` (asserted by platform), `upload.native_usb`, `upload.offset_address`, `build.hwids` for VID/PID (NOT `board_build.vid`). See [arch/samd21.md — PlatformIO Board JSON](arch/samd21.md#platformio-board-json-atmelsam-platform).
> - **ststm32** (STM32): See [arch/stm32.md](arch/stm32.md) for upload and debug specifics.
> - **espressif32** (ESP32): See [arch/esp32.md](arch/esp32.md) for partition table and flash config.

### Registering custom board

Place the JSON in one of these locations:

1. **Project-level**: `boards/seeed_xiao_<chip>.json` (next to `platformio.ini`)
2. **Global-level**: `~/.platformio/boards/seeed_xiao_<chip>.json`

Reference in `platformio.ini`:

```ini
[env:seeed_xiao_<chip>]
board = seeed_xiao_<chip>   ; matches JSON filename without extension
```

## 4. Custom Platform Creation

If the MCU is not supported by any existing platform, create a custom one.

### Platform directory structure

```
platform-<vendor>-<arch>/
├── platform.json           # Platform manifest
├── builder/
│   └── main.py             # Build scripts
├── boards/
│   └── seeed_xiao_<chip>.json
├── frameworks/
│   └── arduino/
│       └── variant.cpp
└── misc/
    └── packages.json       # Toolchain dependencies
```

### platform.json

```json
{
  "name": "<vendor><arch>",
  "title": "<Vendor> <Arch>",
  "description": "Platform for <Vendor> <Arch> MCUs",
  "url": "https://github.com/Seeed-Studio/platform-<vendor>-<arch>",
  "version": "1.0.0",
  "homepage": "https://wiki.seeedstudio.com/",
  "license": "Apache-2.0",
  "engines": {
    "platformio": "^6"
  },
  "packages": {
    "toolchain-<arch>": {
      "type": "toolchain",
      "owner": "platformio",
      "version": "~<version>"
    },
    "framework-arduino-<vendor>": {
      "type": "framework",
      "owner": "Seeed-Studio",
      "version": "https://github.com/Seeed-Studio/...<ref>"
    }
  }
}
```

### Install custom platform

```bash
pio platform install "file:///path/to/platform-<vendor>-<arch>"
```

Or from a Git repository:

```bash
pio platform install "https://github.com/Seeed-Studio/platform-<vendor>-<arch>"
```

## 5. Compile and Upload

### Compile

```bash
pio run -e seeed_xiao_<chip>
```

### Upload

```bash
pio run -e seeed_xiao_<chip> --target upload
```

### Upload with specific port

```bash
pio run -e seeed_xiao_<chip> --target upload --upload-port /dev/ttyUSB0
```

### Clean build

```bash
pio run -e seeed_xiao_<chip> --target clean
```

### Serial monitor

```bash
pio device monitor -e seeed_xiao_<chip>
```

### Compile + upload + monitor

```bash
pio run -e seeed_xiao_<chip> --target upload && pio device monitor
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
| `Unknown board` | Board JSON not found | Check JSON file is in `boards/` dir and name matches `platformio.ini` |
| Build error: undefined `LED_BUILTIN` | Missing variant or macro | Add `build_flags = -DLED_BUILTIN=<pin>` to `platformio.ini` |
| Upload failed: no access | Linux USB permissions | Add user to `dialout` group or use `sudo` |
| `Platform not found` | Platform not installed | Run `pio platform install <platform_name>` |
| Linker error: RAM overflow | Too large for MCU RAM | Optimize code or select a larger RAM variant |
| Wrong flash size | `maximum_size` mismatch | Verify against MCU datasheet and adjust board JSON |
| Chip-specific build error | Missing arch-specific config | See [architecture reference](arch/) for required build flags |
| `AssertionError` (atmelsam) | Missing `openocd_chipname` in board JSON debug section | Add `debug.openocd_chipname` — see [arch/samd21.md](arch/samd21.md#platformio-board-json-atmelsam-platform) |
| `USB_VID`/`USB_PID` not declared (atmelsam) | Used `board_build.vid`/`pid` instead of `build.hwids` | Use `build.hwids` array — see [arch/samd21.md](arch/samd21.md#usb-vidpid-via-buildhwids-not-board_buildvid) |
| `Missed J-Link Device ID` (atmelsam) | Missing `jlink_device` in board JSON debug section | Add `debug.jlink_device` — see [arch/samd21.md](arch/samd21.md#platformio-board-json-atmelsam-platform) |
