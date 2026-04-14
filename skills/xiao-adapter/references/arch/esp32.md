# ESP32 / ESP32-C3 / ESP32-S3 Adaptation Notes

## Core Repository

| Platform | Repository | Notes |
|---|---|---|
| Arduino | `espressif/arduino-esp32` | Supports ESP32, S2, S3, C3, C6 |
| PlatformIO | `platformio/espressif32` | Built-in platform |
| MicroPython | `micropython/ports/esp32` | Requires ESP-IDF |

## GPIO Matrix

ESP32 uses a GPIO matrix that allows most peripherals to be routed to any GPIO pin. This simplifies pin assignment but has caveats:

- **Strapping pins** must be handled carefully — they have default pull-up/down states that affect boot mode
- **Input-only pins** (GPIO34-39 on ESP32) cannot be used as outputs
- **USB pins** (GPIO19/20 on ESP32-C3) are fixed for USB CDC/JTAG

### Strapping Pins (ESP32-C3)

| Pin | Function | Recommended State |
|---|---|---|
| GPIO2 | Strapping (boot mode) | Pull-up via external resistor |
| GPIO8 | Strapping (boot mode) | Pull-down via external resistor |
| GPIO9 | Strapping (JTAG) | Pull-up via external resistor |

### ESP32-C3 USB Pins

| Pin | Function |
|---|---|
| GPIO18 | USB_D+ |
| GPIO19 | USB_D- |

These pins are fixed — USB CDC/JTAG uses them directly, no GPIO matrix routing.

## variant.h Specifics

ESP32 Arduino core uses a different variant structure than SAMD:

```cpp
// No special include needed — Arduino.h works fine on ESP32
#include <stdint.h>

#define BOARD_NAME "Seeed XIAO ESP32C3"
// ... standard defines
```

ESP32 does not use `PinDescription` arrays. Pin mapping is handled by the GPIO matrix in the core.

## MicroPython

- **Port**: `lib/micropython/ports/esp32` (ESP-IDF based)
- **Config style**: Traditional (`mpconfigboard.h`, `mpconfigboard.mk`, `pins.csv`)
- **Pin naming**: `GPIOx` (e.g., `GPIO5`, `GPIO21`)
- **Flash**: esptool (`esptool.py --chip esp32c3 --port /dev/ttyUSB0 write_flash -z 0x0 firmware.bin`)
- **Toolchain**: `xtensa-esp32-elf` or `riscv32-esp-elf` (ESP32-C3)
- **Build**: `make BOARD=ESP32_GENERIC BOARD_DIR=../../../../boards/seeed/xiao_esp32c3`

XIAO ESP32-C3 has existing MicroPython support in Seeed's repo.

| Method | Tool | Command |
|---|---|---|
| Serial (esptool) | `esptool.py` | `esptool.py --chip esp32c3 --port /dev/ttyUSB0 write_flash -z 0x0 firmware.bin` |
| USB DFU (native) | `dfu-util` | `dfu-util -d 303a:4001 -a 0 -D firmware.bin` |
| JTAG | `openocd` | `openocd -f interface/cmsis-dap.cfg -f target/esp32c3.cfg ...` |

## Partition Table

ESP32 requires a partition table for flash layout. For XIAO's typical 4MB flash:

```
# Name,   Type, SubType, Offset,  Size
nvs,      data, nvs,     0x9000,  0x5000
otadata,  data, ota,     0xe000,  0x2000
phy_init, data, phy,     0xf000,  0x1000
ota_0,    app,  ota_0,   0x10000, 0x1E0000
ota_1,    app,  ota_1,   0x1F0000,0x1E0000
spiffs,   data, spiffs,  0x3D0000,0x30000
```

## USB CDC Configuration

For ESP32-C3/S3 native USB CDC:

```
// In sdkconfig or menuconfig:
CONFIG_USB_CDC_ENABLED=y
CONFIG_ESP_CONSOLE_USB_CDC=y
```

## Known Pitfalls

| Problem | Cause | Solution |
|---|---|---|
| Boot loop | Strapping pin misconfigured | Check pull-up/down on strapping pins |
| USB not enumerated | Missing `CONFIG_USB_CDC_ENABLED` | Enable in sdkconfig/menuconfig |
| GPIO34-39 output fails | Input-only pins on ESP32 | Use GPIO0-33 for output |
| Flash too large | Partition table misconfigured | Adjust partition sizes for XIAO flash size |
