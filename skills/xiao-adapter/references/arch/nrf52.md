# nRF52 / nRF52840 Adaptation Notes

## Core Repository

| Platform | Repository | Notes |
|---|---|---|
| Arduino | `arduino/ArduinoCore-nRF528x-mbedos` | Based on mbed-os |
| PlatformIO | `platformio/nordicnrf52` | Built-in platform |
| MicroPython | `micropython/ports/nrf` | Dedicated nRF52 port |

## PSEL Register Pin Configuration

nRF52 uses PSEL (Peripheral Select) registers to assign pins to peripherals. Any GPIO can be assigned to any peripheral via PSEL registers — similar to ESP32's GPIO matrix but simpler.

### PSEL Register Pattern

```c
// Example: Configure UART0 pins
NRF_UARTE0->PSEL.TXD = (pin << UARTE_PSEL_TXD_PIN_Pos) | (port << UARTE_PSEL_TXD_PORT_Pos);
NRF_UARTE0->PSEL.RXD = (pin << UARTE_PSEL_RXD_PIN_Pos) | (port << UARTE_PSEL_RXD_PORT_Pos);
```

## SoftDevice

nRF52840 typically runs Nordic's SoftDevice (Bluetooth stack). This reserves certain resources:

| Resource | Reserved by SoftDevice |
|---|---|
| Flash | Bottom ~100KB (varies by SD version) |
| RAM | Top ~64KB (varies by SD version) |
| Timer0 | Used by SoftDevice |
| RADIO | Used by SoftDevice |

Adjust linker script and RAM allocation when using SoftDevice.

## variant.h Specifics

The nRF528x Arduino core is mbed-based:

```cpp
#include <Arduino.h>  // mbed-based, Arduino.h is fine

#define BOARD_NAME "Seeed XIAO nRF52840"
// ... standard defines
```

## Upload / Debug

| Method | Tool | Command |
|---|---|---|
| DFU (OTA) | `adafruit-nrfutil` | `adafruit-nrfutil dfu serial -pkg firmware.zip -p /dev/ttyACM0 -b 115200` |
| SWD (OpenOCD) | `openocd` | `openocd -f interface/cmsis-dap.cfg -f target/nrf52.cfg ...` |
| J-Link | `nrfjprog` | `nrfjprog --program firmware.hex --chiperase --verify --reset` |

## Known Pitfalls

| Problem | Cause | Solution |
|---|---|---|
| Flash overflow | SoftDevice reserves too much | Adjust linker script start address and RAM size |
| BLE not working | SoftDevice not flashed | Flash SoftDevice hex first, then application |
| Hard fault | RAM overlap with SoftDevice | Reduce application RAM in linker script |
| USB not enumerated | USB pins not configured | Enable USB in board config, check D+/D- pin PSEL |
