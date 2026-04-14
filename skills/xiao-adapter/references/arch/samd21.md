# SAMD21 / SAMD51 Adaptation Notes

## Core Repository

| Platform | Repository | Notes |
|---|---|---|
| Arduino | `Seeed-Studio/ArduinoCore-samd` | Use Seeed's fork, not official Arduino repo |
| PlatformIO | `platformio/atmelsam` | Built-in platform |
| MicroPython | `micropython/ports/stm32` (shared ARM Cortex-M port) | SAMD support via `ports/stm32` |

## variant.h Specifics

SAMD variant files **must NOT include `Arduino.h`** — this causes a circular dependency. Instead, include `WVariant.h` which provides `PinDescription`, `EPortType`, `EPioType`:

```cpp
#include <stdint.h>
#include <WVariant.h>   // NOT Arduino.h — provides PinDescription, EPortType, EPioType
```

`WVariant.h` is part of the SAMD core and defines all types needed by variant.h/variant.cpp.

## Pin Description (variant.cpp)

SAMD uses a `PinDescription` array in `variant.cpp` to map Arduino pins to MCU peripherals:

```cpp
#include <WVariant.h>

const PinDescription g_APinDescription[] = {
  { PORTA, 10, PIO_SERCOM, (PIN_ATTR_DIGITAL|PIN_ATTR_PWM|PIN_ATTR_TIMER), No_ADC_Channel, NOT_ON_PWM, NOT_ON_TIMER, EXTERNAL_INT_10 },
  // ... more pins
};
```

### PinDescription Fields

| Field | Description |
|---|---|
| `ulPort` | GPIO port (`PORTA` or `PORTB`) |
| `ulPin` | Pin number (0-31) |
| `ulPinType` | `PIO_SERCOM`, `PIO_SERCOM_ALT`, `PIO_TIMER`, `PIO_PWM`, `PIO_GPIO`, etc. |
| `ulPinAttribute` | Bitmask: `PIN_ATTR_DIGITAL`, `PIN_ATTR_PWM`, `PIN_ATTR_TIMER`, `PIN_ATTR_ANALOG` |
| `ulPinMode` | ADC channel number or `No_ADC_Channel` |
| `ulPinConfig` | PWM/TC config (`NOT_ON_PWM` / `NOT_ON_TIMER` or channel) |

## SERCOM Pin Mux

SAMD21 has 6 SERCOM instances. Each SERCOM pad (0-3) maps to specific MCU pins. Two pin function types exist:

| Type | Description |
|---|---|
| `PIO_SERCOM` | Primary SERCOM pin function |
| `PIO_SERCOM_ALT` | Alternate SERCOM pin function |

A pin used for SERCOM must specify which SERCOM instance and pad in `variant.cpp`. For example, to use PA10 as SERCOM0 PAD2:

```cpp
{ PORTA, 10, PIO_SERCOM, (PIN_ATTR_DIGITAL), No_ADC_Channel, NOT_ON_PWM, NOT_ON_TIMER, EXTERNAL_INT_10 },
// Then configure: SERCOM0->PAD[2] = PINMUX_PA10C_SERCOM0_PAD2
```

### Common SERCOM Pin Assignments for XIAO

| Function | Typical Pin | SERCOM | Pad | Pinmux |
|---|---|---|---|---|
| UART RX | PA11 | SERCOM0 | PAD3 | `PINMUX_PA11C_SERCOM0_PAD3` |
| UART TX | PA10 | SERCOM0 | PAD2 | `PINMUX_PA10C_SERCOM0_PAD2` |
| I2C SDA | PA22 | SERCOM3 | PAD0 | `PINMUX_PA22C_SERCOM3_PAD0` |
| I2C SCL | PA23 | SERCOM3 | PAD1 | `PINMUX_PA23C_SERCOM3_PAD1` |

## PWM/TC Channel Reference

SAMD21 has:
- **TCC0, TCC1, TCC2** (Timer/Counter for Control — up to 24-bit, multiple channels)
- **TC3, TC4, TC5** (Basic Timer/Counter — 16-bit, single channel each)
- **No TCC3 or TC0/TC1/TC2** — these do not exist on SAMD21

### PWM Naming Convention (Critical)

The SAMD core uses `PWM<x>_CH<y>` aliases for the `ulPinConfig` field in `PinDescription`. **Do NOT confuse these with the TC/TCC naming**:

| PWM Alias | Actual Timer | Available Channels |
|---|---|---|
| `PWM0` | TCC0 | CH0–CH7 (8 channels) |
| `PWM1` | TCC1 | CH0–CH3 (4 channels) |
| `PWM2` | TCC2 | CH0–CH3 (4 channels) |
| `PWM3` | TC3 | CH0–CH1 (**only 2 channels, no CH2/CH3!**) |
| `PWM4` | TC4 | CH0–CH1 (**only 2 channels, no CH2/CH3!**) |
| `PWM5` | TC5 | CH0–CH1 (**only 2 channels, no CH2/CH3!**) |

The `ulTCChannel` field uses direct TC/TCC names:

| TC/TCC Name | Channels |
|---|---|
| `TCC0_CH0` – `TCC0_CH7` | 8 channels |
| `TCC1_CH0` – `TCC1_CH3` | 4 channels |
| `TCC2_CH0` – `TCC2_CH3` | 4 channels |
| `TC3_CH0`, `TC3_CH1` | **2 channels only** |
| `TC4_CH0`, `TC4_CH1` | **2 channels only** |
| `TC5_CH0`, `TC5_CH1` | **2 channels only** |

### Pin-to-PWM/TC Channel Mapping

| Pin | Timer/Counter | PWM Alias | TC/TCC Name |
|---|---|---|---|
| PA04 | TCC0 CH0 | `PWM0_CH0` | `TCC0_CH0` |
| PA05 | TCC0 CH1 | `PWM0_CH1` | `TCC0_CH1` |
| PA06 | TCC1 CH0 | `PWM1_CH0` | `TCC1_CH0` |
| PA07 | TCC1 CH1 | `PWM1_CH1` | `TCC1_CH1` |
| PA08 | TCC0 CH2 | `PWM0_CH2` | `TCC0_CH2` |
| PA09 | TCC0 CH3 | `PWM0_CH3` | `TCC0_CH3` |
| PA10 | TCC0 CH4 | `PWM0_CH4` | `TCC0_CH4` |
| PA11 | TCC0 CH5 | `PWM0_CH5` | `TCC0_CH5` |
| PA12 | TCC0 CH6 | `PWM0_CH6` | `TCC0_CH6` |
| PA13 | TCC0 CH7 | `PWM0_CH7` | `TCC0_CH7` |
| PA14 | TC3 CH0 | `PWM3_CH0` | `TC3_CH0` |
| PA15 | TC3 CH1 | `PWM3_CH1` | `TC3_CH1` |
| PA16 | TCC1 CH2 | `PWM1_CH2` | `TCC1_CH2` |
| PA17 | TCC1 CH3 | `PWM1_CH3` | `TCC1_CH3` |
| PA18 | TC3 CH0 | `PWM3_CH0` | `TC3_CH0` |
| PA19 | TC3 CH1 | `PWM3_CH1` | `TC3_CH1` |
| PA20 | TCC0 CH4 | `PWM0_CH4` | `TCC0_CH4` |
| PA21 | TCC0 CH5 | `PWM0_CH5` | `TCC0_CH5` |
| PA22 | TCC0 CH4 / TCC1 CH0 | `PWM0_CH4` / `PWM1_CH0` | `TCC0_CH4` / `TCC1_CH0` |
| PA23 | TCC0 CH5 / TCC1 CH1 | `PWM0_CH5` / `PWM1_CH1` | `TCC0_CH5` / `TCC1_CH1` |
| PA24 | TCC1 CH2 | `PWM1_CH2` | `TCC1_CH2` |
| PA25 | TCC1 CH3 | `PWM1_CH3` | `TCC1_CH3` |

> **Important**: PA20/PA21 share TCC0 CH4/CH5 with PA10/PA11. Each channel can only drive one pin at a time. The same pin can route to multiple timers (e.g., PA18 to both TC3 CH0 and TCC1 CH2) — choose one based on application needs.

### Setting PWM in PinDescription

Use the table above to look up the correct `PWM<x>_CH<y>` and `TCCx_CHy` / `TCx_CHy` values for each pin. Example for PA04:

```cpp
// PA04 → TCC0 CH0 → PWM0_CH0, TCC0_CH0
{ PORTA, 4, PIO_TIMER, (PIN_ATTR_DIGITAL|PIN_ATTR_PWM|PIN_ATTR_TIMER), No_ADC_Channel, PWM0_CH0, TCC0_CH0, EXTERNAL_INT_4 },
```

**Common mistake**: Assigning PA20 to `PWM3_CH2` or `TC3_CH2` — TC3 only has CH0 and CH1! PA20 routes to TCC0 CH4 (`PWM0_CH4, TCC0_CH4`).

## ADC Channel Mapping

SAMD21 ADC channels are **not sequential** with pin numbers:

| Pin | ADC Channel |
|---|---|
| PA02 | CH0 |
| PA03 | CH1 |
| PA04 | CH4 |
| PA05 | CH5 |
| PA06 | CH6 |
| PA07 | CH7 |
| PA08 | CH8 |
| PA09 | CH9 |
| PA10 | CH10 |
| PA11 | CH11 |
| PA12 | CH12 |
| PA13 | CH13 |
| PA14 | CH14 |
| PA15 | CH15 |
| PA16 | CH16 |
| PA17 | CH17 |
| PA18 | CH18 |
| PA19 | CH19 |

Use `ADC_Channel<x>` (e.g., `ADC_Channel0`) for the `ulPinMode` field in PinDescription.

## Upload / Debug

| Method | Tool | Command |
|---|---|---|
| Bootloader (bossac) | `bossac` | `bossac -i -d -U true -i -e -w -v <firmware.bin> -R` |
| SWD (OpenOCD) | `openocd` | `openocd -f interface/cmsis-dap.cfg -f target/at91samdXX.cfg -c "program ..."` |
| SWD (Atmel ICE) | `openocd` | `openocd -f interface/atmel-ice.cfg -f target/at91samdXX.cfg ...` |

The XIAO SAMD21 ships with a UF2-compatible bootloader. Double-tap reset to enter bootloader mode, then drag-and-drop UF2 or use bossac.

## Known Pitfalls

| Problem | Cause | Solution |
|---|---|---|
| `PinDescription` not found | Included `Arduino.h` instead of `WVariant.h` in variant.h | Change to `#include <WVariant.h>` |
| Circular include error | variant.h includes Arduino.h which includes variant.h | Include `WVariant.h` directly |
| Invalid PWM/TC channel | Used non-existent `TC0`/`TC1`/`TCC3` or `PWM3_CH2`/`PWM3_CH3` | Use the PWM naming table above — TC3/4/5 only have CH0-CH1 |
| Wrong PWM alias for pin | Used `PWM3` when pin routes to TCC0 | Always look up pin → PWM alias in the Pin-to-PWM table |
| SERCOM not working | Wrong `PIO_SERCOM` vs `PIO_SERCOM_ALT` | Check datasheet pin mux table for the specific pin |
| ADC reads wrong channel | Assumed sequential channel mapping | Use the ADC channel table above — channels skip 2-3 and 12-15 |
| Wrong SERCOM instance | Pad assigned to wrong SERCOM | Verify SERCOM pad mux in datasheet Section "Multiplexed Signals" |

## variant.cpp Validation Checklist

After generating `variant.cpp`, verify **every** PWM-capable pin against the Pin-to-PWM table above:

1. **Check `ulPinConfig` (PWM field)**: Must be `PWM0_CHx`–`PWM5_CHx`. Verify the PWM alias matches the pin's timer (e.g., PA20 → `PWM0_CH4`, NOT `PWM3_CH2`).
2. **Check `ulTCChannel` (TC field)**: Must be `TCCx_CHy` or `TCx_CHy`. Verify TC channels: TC3/TC4/TC5 only have CH0 and CH1.
3. **Check ADC channels**: For every pin with `PIO_ANALOG`, verify the ADC channel matches the ADC Channel Mapping table. PA02=CH0, PA04=CH4 (NOT CH2), etc.
4. **Check `#include`**: `variant.h` must include `<WVariant.h>`, NOT `<Arduino.h>`.
5. **Check `g_apTCInstances`**: Must be `{ TCC0, TCC1, TCC2, TC3, TC4, TC5 }` — no TC0, TC1, TC2, no TCC3.
6. **Check SERCOM types**: Verify `PIO_SERCOM` vs `PIO_SERCOM_ALT` matches the pin mux table in the datasheet.
