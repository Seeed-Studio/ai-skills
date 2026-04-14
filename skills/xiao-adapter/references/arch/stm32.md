# STM32 (F1/F4/H7, GD32) Adaptation Notes

## Core Repository

| Platform | Repository | Notes |
|---|---|---|
| Arduino | `stm32duino/Arduino_Core_STM32` | Supports F1/F2/F3/F4/F7/G0/G4/H7/L0/L1/L4/U5, GD32 |
| PlatformIO | `platformio/ststm32` | Built-in platform |
| MicroPython | `micropython/ports/stm32` | Primary ARM Cortex-M port |

## AF Mapping (Alternate Function)

STM32 uses AF (Alternate Function) pin mapping. Each pin can have up to 16 alternate functions (AF0-AF15). The correct AF must be configured for each peripheral.

### Example: STM32F103 AF Table

| Pin | AF | Peripheral |
|---|---|---|
| PA9 | AF1 | USART1_TX |
| PA10 | AF1 | USART1_RX |
| PB6 | AF1 | I2C1_SCL |
| PB7 | AF1 | I2C1_SDA |
| PA5 | AF5 | SPI1_SCK |
| PA6 | AF5 | SPI1_MISO |
| PA7 | AF5 | SPI1_MOSI |

## variant.h Specifics

STM32duino uses a standard variant structure:

```cpp
#include <Arduino.h>  // Arduino.h is fine for STM32

#define BOARD_NAME "Seeed XIAO STM32F103"
// ... standard defines
```

STM32 uses `PinName` and `PinMap` arrays in the core for pin configuration, not a `PinDescription` array like SAMD.

## HAL Configuration

STM32duino relies on STM32 HAL. Key configuration files:

| File | Purpose |
|---|---|
| `stm32_def_build_info.h` | MCU selection, HAL config |
| `stm32yyxx_hal_conf.h` | Peripheral HAL enables/disables |
| `system_stm32yyxx.c` | Clock configuration |
| `ld/stm32yyxx_<flash>.ld` | Linker script for memory layout |

## MicroPython

- **Port**: `lib/micropython/ports/stm32` (primary ARM Cortex-M port)
- **Config style**: Traditional (`mpconfigboard.h`, `mpconfigboard.mk`, `pins.csv`)
- **Pin naming**: `PAxx` (e.g., `PA9`, `PB6`)
- **Flash**: OpenOCD (SWD), STM32CubeProgrammer, or dfu-util (DFU)
- **Toolchain**: `gcc-arm-none-eabi`
- **Build**: `make BOARD=SEEED_XIAO_STM32F103 BOARD_DIR=../../../../boards/seeed/xiao_stm32f103`

The stm32 port is MicroPython's most mature ARM Cortex-M port and serves as the base for many MCUs including SAMD21 and GD32.

| Method | Tool | Command |
|---|---|---|
| SWD (OpenOCD) | `openocd` | `openocd -f interface/cmsis-dap.cfg -f target/stm32f1x.cfg -c "program ..."` |
| ST-Link | `openocd` | `openocd -f interface/stlink.cfg -f target/stm32f1x.cfg ...` |
| STM32CubeProgrammer | GUI | Select hex file, click Download |
| Serial (DFU) | `dfu-util` | `dfu-util -a 0 -D firmware.bin` (enter DFU mode first) |

## Known Pitfalls

| Problem | Cause | Solution |
|---|---|---|
| Wrong clock speed | `HSE_VALUE` mismatch | Set correct crystal frequency in build flags |
| HAL driver missing | Peripheral not enabled in HAL conf | Add `#define HAL_<PERIPH>_MODULE_ENABLED` |
| Hard fault on boot | Linker script flash/RAM mismatch | Use correct ld file for target MCU variant |
| USB not working | Missing USB HAL or wrong pins | Enable `HAL_PCD_MODULE_ENABLED`, check USB DP/DN pins |
