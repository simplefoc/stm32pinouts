---
layout: default
grand_parent: STM32 Family Pinout
parent: STM32F3xx Family Pinout
title: F303C(B-C)T Pinout
has_toc: false
has_children: false
---

## PWM Timer Pins

| Pin | PWM Timer | Channel | BLACKPILL_F303CC | generic | SPARKY_F303CC |
| --- | --- | --- | --- | --- | --- |
| PA_0 | TIM2 | 1 | D20/A0 | D0/A0 | D20/A0 |
| PA_1 | TIM2 | 2 | D21/A1 | D1/A1 | D21/A1 |
| PA_1_ALT1 | TIM15 | 1N | - | - | - |
| PA_2 | TIM2 | 3 | D22/A2 | D2/A2 | D22/A2 |
| PA_2_ALT1 | TIM15 | 1 | - | - | - |
| PA_3 | TIM2 | 4 | D23/A3 | D3/A3 | D23/A3 - RCX |
| PA_3_ALT1 | TIM15 | 2 | - | - | - |
| PA_4 | TIM3 | 2 | D24/A4 | D4/A4 | D24/A4 |
| PA_5 | TIM2 | 1 | D25/A5 | D5/A5 | D25/A5 |
| PA_6 | TIM3 | 1 | D26/A6 | D6/A6 | D26/A6 |
| PA_6_ALT1 | TIM16 | 1 | - | - | - |
| PA_7 | TIM1 | 1N | D27/A7 | D7/A7 | D27/A7 |
| PA_7_ALT1 | TIM3 | 2 | - | - | - |
| PA_7_ALT2 | TIM8 | 1N | - | - | - |
| PA_7_ALT3 | TIM17 | 1 | - | - | - |
| PA_8 | TIM1 | 1 | D12 | D8 | D12 |
| PA_9 | TIM1 | 2 | D11 | D9 | D11 - SCL MPU-9150 |
| PA_9_ALT1 | TIM2 | 3 | - | - | - |
| PA_10 | TIM1 | 3 | D10 | D10 | D10 - SDA MPU-9150 |
| PA_10_ALT1 | TIM2 | 4 | - | - | - |
| PA_11 | TIM1 | 1N | D9  - USB_DM | D11 | D9  - USB_DM |
| PA_11_ALT1 | TIM1 | 4 | - | - | - |
| PA_11_ALT2 | TIM4 | 1 | - | - | - |
| PA_12 | TIM1 | 2N | D8  - USB_DP | D12 | D8  - USB_DP |
| PA_12_ALT1 | TIM4 | 2 | - | - | - |
| PA_12_ALT2 | TIM16 | 1 | - | - | - |
| PA_13 | TIM4 | 3 | D33 - SWDI0 | D13 | D33 - SWDI0 |
| PA_13_ALT1 | TIM16 | 1N | - | - | - |
| PA_14 | TIM8 | 2 | D34 - SWCLK | D14 | D34 - SWCLK |
| PA_15 | TIM2 | 1 | D7 | D15 | D7 |
| PA_15_ALT1 | TIM8 | 1 | - | - | - |
| PB_0 | TIM1 | 2N | D28/A8 | D16/A8 | D28/A8 |
| PB_0_ALT1 | TIM3 | 3 | - | - | - |
| PB_0_ALT2 | TIM8 | 2N | - | - | - |
| PB_1 | TIM1 | 3N | D29/A9 | D17/A9 | D29/A9 |
| PB_1_ALT1 | TIM3 | 4 | - | - | - |
| PB_1_ALT2 | TIM8 | 3N | - | - | - |
| PB_3 | TIM2 | 2 | D6 | D19 | D6 |
| PB_3_ALT1 | TIM8 | 1N | - | - | - |
| PB_4 | TIM3 | 1 | D5 | D20 | D5  - LED_BLUE |
| PB_4_ALT1 | TIM8 | 2N | - | - | - |
| PB_4_ALT2 | TIM16 | 1 | - | - | - |
| PB_5 | TIM3 | 2 | D4 | D21 | D4  - LED_RED |
| PB_5_ALT1 | TIM8 | 3N | - | - | - |
| PB_5_ALT2 | TIM17 | 1 | - | - | - |
| PB_6 | TIM4 | 1 | D3 | D22 | D3  - UART1_TX or I2C1_SCL |
| PB_6_ALT1 | TIM8 | 1 | - | - | - |
| PB_6_ALT2 | TIM16 | 1N | - | - | - |
| PB_7 | TIM3 | 4 | D2 | D23 | D2  - UART1_RX or I2C1_SDC |
| PB_7_ALT1 | TIM4 | 2 | - | - | - |
| PB_7_ALT2 | TIM17 | 1N | - | - | - |
| PB_8 | TIM4 | 3 | D1 | D24 | D1  - CAN_RX |
| PB_8_ALT1 | TIM8 | 2 | - | - | - |
| PB_8_ALT2 | TIM16 | 1 | - | - | - |
| PB_9 | TIM4 | 4 | D0 | D25 | D0  - CAN_TX |
| PB_9_ALT1 | TIM8 | 3 | - | - | - |
| PB_9_ALT2 | TIM17 | 1 | - | - | - |
| PB_10 | TIM2 | 3 | D30 | D26 | D30 - UART3_TX |
| PB_11 | TIM2 | 4 | D31 | D27 | D31 - UART3_RX |
| PB_13 | TIM1 | 1N | D15/A12 | D29/A12 | D15/A12 |
| PB_14 | TIM1 | 2N | D14/A13 | D30/A13 | D14/A13 |
| PB_14_ALT1 | TIM15 | 1 | - | - | - |
| PB_15 | TIM1 | 3N | D13/A14 | D31/A14 | D13/A14 |
| PB_15_ALT1 | TIM15 | 1N | - | - | - |
| PB_15_ALT2 | TIM15 | 2 | - | - | - |
| PC_13 | TIM1 | 1N | D17 - LED | D32 | D17 - LED on Bluepill Board |
| PF_0 | TIM1 | 3N | D35 - OSC IN | D35 | D35 - OSC IN |


## ADC Pins

| Pin | ADC | Channel | BLACKPILL_F303CC | generic | SPARKY_F303CC |
| --- | --- | --- | --- | --- | --- |
| PA_0 | ADC1 | 1 | D20/A0 | D0/A0 | D20/A0 |
| PA_1 | ADC1 | 2 | D21/A1 | D1/A1 | D21/A1 |
| PA_2 | ADC1 | 3 | D22/A2 | D2/A2 | D22/A2 |
| PA_3 | ADC1 | 4 | D23/A3 | D3/A3 | D23/A3 - RCX |
| PA_4 | ADC2 | 1 | D24/A4 | D4/A4 | D24/A4 |
| PA_5 | ADC2 | 2 | D25/A5 | D5/A5 | D25/A5 |
| PA_6 | ADC2 | 3 | D26/A6 | D6/A6 | D26/A6 |
| PA_7 | ADC2 | 4 | D27/A7 | D7/A7 | D27/A7 |
| PB_0 | ADC3 | 12 | D28/A8 | D16/A8 | D28/A8 |
| PB_1 | ADC3 | 1 | D29/A9 | D17/A9 | D29/A9 |
| PB_2 | ADC2 | 12 | D32/A10 - BOOT1 | D18/A10 | D32/A10 - BOOT1 |
| PB_12 | ADC4 | 3 | D16/A11 | D28/A11 | D16/A11 |
| PB_13 | ADC3 | 5 | D15/A12 | D29/A12 | D15/A12 |
| PB_14 | ADC4 | 4 | D14/A13 | D30/A13 | D14/A13 |
| PB_15 | ADC4 | 5 | D13/A14 | D31/A14 | D13/A14 |


[Back to Main Page](../../)