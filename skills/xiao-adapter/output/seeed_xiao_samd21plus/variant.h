#pragma once
// The definitions here needs a SAMD core >=1.6.10
#define ARDUINO_SAMD_VARIANT_COMPLIANCE 10610
#include "Arduino.h"

// Frequency of the board main oscillator
#define VARIANT_MAINOSC (32768ul)

// Master clock frequency
#define VARIANT_MCK (F_CPU)

// Pins
// ----
// Number of pins defined in PinDescription array
#define PINS_COUNT           (30u)
#define NUM_DIGITAL_PINS     (30u)
#define NUM_ANALOG_INPUTS    (11u)
#define NUM_ANALOG_OUTPUTS   (1u)

// Low-level pin register query macros
#define digitalPinToPort(P)        (&(PORT->Group[g_APinDescription[P].ulPort]))
#define digitalPinToBitMask(P)     (1 << g_APinDescription[P].ulPin)
#define portOutputRegister(port)   (&(port->OUT.reg))
#define portInputRegister(port)    (&(port->IN.reg))
#define portModeRegister(port)     (&(port->DIR.reg))
#define digitalPinHasPWM(P)        (g_APinDescription[P].ulPWMChannel != NOT_ON_PWM || g_APinDescription[P].ulTCChannel != NOT_ON_TIMER)

// LEDs
// ----
// PA27 - RGB LED (from schematic)
#define PIN_LED_13       (13u)
#define PIN_LED          PIN_LED_13
#define LED_BUILTIN      PIN_LED

/*
 * Analog pins
 * A0-A3: shared with D0-D3 (castellated pads)
 * A4-A9: additional ADC-capable pins
 * A10: VBAT monitor (PB3)
 */
#define PIN_A0   (0ul)
#define PIN_A1   (PIN_A0 + 1)
#define PIN_A2   (PIN_A0 + 2)
#define PIN_A3   (PIN_A0 + 3)
#define PIN_A4   (PIN_A0 + 4)
#define PIN_A5   (PIN_A0 + 5)
#define PIN_A6   (PIN_A0 + 6)
#define PIN_A7   (PIN_A0 + 7)
#define PIN_A8   (PIN_A0 + 8)
#define PIN_A9   (PIN_A0 + 9)
#define PIN_A10  (PIN_A0 + 10)

#define PIN_DAC0 (PIN_A0)

static const uint8_t A0 = PIN_A0;
static const uint8_t A1 = PIN_A1;
static const uint8_t A2 = PIN_A2;
static const uint8_t A3 = PIN_A3;
static const uint8_t A4 = PIN_A4;
static const uint8_t A5 = PIN_A5;
static const uint8_t A6 = PIN_A6;
static const uint8_t A7 = PIN_A7;
static const uint8_t A8 = PIN_A8;
static const uint8_t A9 = PIN_A9;
static const uint8_t A10 = PIN_A10;

static const uint8_t DAC0 = PIN_DAC0;

#define ADC_RESOLUTION 12

// Digital pins - XIAO castellated pads (D0-D10)
#define D0  (0u)
#define D1  (1u)
#define D2  (2u)
#define D3  (3u)
#define D4  (4u)
#define D5  (5u)
#define D6  (6u)
#define D7  (7u)
#define D8  (8u)
#define D9  (9u)
#define D10 (10u)

// Extended pins (D12-D27)
#define D12 (12u)
#define D13 (13u)
#define D14 (14u)
#define D15 (15u)
#define D16 (16u)
#define D17 (17u)
#define D18 (18u)
#define D19 (19u)
#define D20 (20u)
#define D21 (21u)
#define D22 (22u)
#define D23 (23u)
#define D24 (24u)
#define D25 (25u)
#define D26 (26u)
#define D27 (27u)

// User Button (PB22, from schematic)
#define PIN_BUTTON       (28u)
#define BUTTON_PULLUP    INPUT_PULLUP

/*
 * SPI Interfaces - SERCOM0
 * MISO: PA05 (D9/A9), MOSI: PA06 (D10/A10), SCK: PA07 (D8/A8)
 */
#define SPI_INTERFACES_COUNT 1

#define PIN_SPI_MISO  (9u)
#define PIN_SPI_SCK   (8u)
#define PIN_SPI_MOSI  (10u)
#define PERIPH_SPI     sercom0
#define PAD_SPI_TX     SPI_PAD_2_SCK_3
#define PAD_SPI_RX     SERCOM_RX_PAD_1

static const uint8_t SS   = 4;   // SPI CS not dedicated, use D4 as default
static const uint8_t MOSI = PIN_SPI_MOSI;
static const uint8_t MISO = PIN_SPI_MISO;
static const uint8_t SCK  = PIN_SPI_SCK;

/*
 * Wire Interfaces - SERCOM2 (external I2C)
 * SDA: PA08 (D4/A4/SDA0), SCL: PA09 (D5/A5/SCL0)
 */
#define WIRE_INTERFACES_COUNT 2

#define PIN_WIRE_SDA   (4u)
#define PIN_WIRE_SCL   (5u)
#define PERIPH_WIRE    sercom2
#define WIRE_IT_HANDLER SERCOM2_Handler

static const uint8_t SDA = PIN_WIRE_SDA;
static const uint8_t SCL = PIN_WIRE_SCL;

// Second I2C - SERCOM1 (PA16/PA17, from schematic)
#define PIN_WIRE1_SDA  (16u)
#define PIN_WIRE1_SCL  (17u)
#define PERIPH_WIRE1   sercom1
#define WIRE1_IT_HANDLER SERCOM1_Handler

// USB - PA33/PA34 (from schematic)
#define PIN_USB_HOST_ENABLE (14ul)
#define PIN_USB_DM          (15ul)
#define PIN_USB_DP          (16ul)

// I2S Interfaces
#define I2S_INTERFACES_COUNT 1

// Serial ports
#ifdef __cplusplus
#include "SERCOM.h"

extern SERCOM sercom0;
extern SERCOM sercom1;
extern SERCOM sercom2;
extern SERCOM sercom3;
extern SERCOM sercom4;
extern SERCOM sercom5;

// Serial1 - SERCOM4 (PB08 TX / PB09 RX, from schematic)
#include "Uart.h"

extern Uart Serial1;
#define PIN_SERIAL1_TX       (6ul)
#define PIN_SERIAL1_RX       (7ul)
#define PAD_SERIAL1_TX       (UART_TX_PAD_0)
#define PAD_SERIAL1_RX       (SERCOM_RX_PAD_1)

#endif // __cplusplus

#define SERIAL_PORT_USBVIRTUAL  Serial
#define SERIAL_PORT_MONITOR     Serial
#define SERIAL_PORT_HARDWARE    Serial1
#define SERIAL_PORT_HARDWARE_OPEN Serial1
