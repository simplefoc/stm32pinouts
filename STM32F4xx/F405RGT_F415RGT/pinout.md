---
layout: default
grand_parent: STM32 Family Pinout
parent: STM32F4xx Family Pinout
title: F405RGT_F415RGT Pinout
has_toc: false
has_children: false
---

## PWM Timer Pins

| Pin | PWM Timer | Channel | FEATHER_F405 | generic | MICROMOD_F405 |
| --- | --- | --- | --- | --- | --- |
| PA_0 | TIM2 | 1 | - | D0/A0 | G2 |
| PA_0_ALT1 | TIM5 | 1 | - | - | - |
| PA_1 | TIM2 | 2 | - | D1/A1 | BATT_VIN/3 |
| PA_1_ALT1 | TIM5 | 2 | - | - | - |
| PA_2 | TIM2 | 3 | - | D2/A2 | TX1 |
| PA_2_ALT1 | TIM5 | 3 | - | - | - |
| PA_2_ALT2 | TIM9 | 1 | - | - | - |
| PA_3 | TIM2 | 4 | D22 - A6 | D3/A3 | RX1 |
| PA_3_ALT1 | TIM5 | 4 | - | - | - |
| PA_3_ALT2 | TIM9 | 2 | - | - | - |
| PA_5 | TIM2 | 1 | PA_5 | D5/A5 | SCK |
| PA_5_ALT1 | TIM8 | 1N | - | - | - |
| PA_6 | TIM3 | 1 | PA_6 | D6/A6 | CIPO |
| PA_6_ALT1 | TIM13 | 1 | - | - | - |
| PA_7 | TIM1 | 1N | PA_7 | D7/A7 | COPI |
| PA_7_ALT1 | TIM3 | 2 | - | - | - |
| PA_7_ALT2 | TIM8 | 1N | - | - | - |
| PA_7_ALT3 | TIM14 | 1 | - | - | - |
| PA_8 | TIM1 | 1 | - | D8 | G1 |
| PA_9 | TIM1 | 2 | - | D9 | - |
| PA_10 | TIM1 | 3 | - | D10 | - |
| PA_11 | TIM1 | 4 | D35 D+ | D11 | D+ |
| PA_15 | TIM2 | 1 | D7 | D15 | STAT |
| PB_0 | TIM1 | 2N | - | D16/A8 | A1 |
| PB_0_ALT1 | TIM3 | 3 | - | - | - |
| PB_0_ALT2 | TIM8 | 2N | - | - | - |
| PB_1 | TIM1 | 3N | - | D17/A9 | INT |
| PB_1_ALT1 | TIM3 | 4 | - | - | - |
| PB_1_ALT2 | TIM8 | 3N | - | - | - |
| PB_3 | TIM2 | 2 | PB_3 | D19 | AUD_BCLK |
| PB_4 | TIM3 | 1 | PB_4 | D20 | AUD_OUT |
| PB_5 | TIM3 | 2 | PB_5 | D21 | AUD_IN |
| PB_6 | TIM4 | 1 | D15 SCL | D22 | SCL1 |
| PB_7 | TIM4 | 2 | D14 SDA | D23 | SDA1 |
| PB_8 | TIM4 | 3 | PB_8 | D24 | CAN_RX |
| PB_8_ALT1 | TIM10 | 1 | - | - | - |
| PB_9 | TIM4 | 4 | PB_9 | D25 | CAN_TX |
| PB_9_ALT1 | TIM11 | 1 | - | - | - |
| PB_10 | TIM2 | 3 | PB_10 | D26 | SCL |
| PB_11 | TIM2 | 4 | D0 | D27 | SDA |
| PB_13 | TIM1 | 1N | D23 SCK | D29 | G10 HOST_VBUS |
| PB_14 | TIM1 | 2N | D24 MISO | D30 | HOST_D- |
| PB_14_ALT1 | TIM8 | 2N | - | - | - |
| PB_14_ALT2 | TIM12 | 1 | - | - | - |
| PB_15 | TIM1 | 3N | D25 MOSI | D31 | HOST_D+ |
| PB_15_ALT1 | TIM8 | 3N | - | - | - |
| PB_15_ALT2 | TIM12 | 2 | - | - | - |
| PC_6 | TIM3 | 1 | PC_6 | D38 | PWM0 |
| PC_6_ALT1 | TIM8 | 1 | - | - | - |
| PC_7 | TIM3 | 2 | PC_7 | D39 | PWM1 |
| PC_7_ALT1 | TIM8 | 2 | - | - | - |
| PC_8 | TIM3 | 3 | D26 SDIO | D40 | G3 |
| PC_8_ALT1 | TIM8 | 3 | - | - | - |
| PC_9 | TIM3 | 4 | PC_9 | D41 | G4 |
| PC_9_ALT1 | TIM8 | 4 | - | - | - |


## ADC Pins

| Pin | ADC | Channel | FEATHER_F405 | generic | MICROMOD_F405 |
| --- | --- | --- | --- | --- | --- |
| PA_0 | ADC1 | 0 | - | D0/A0 | G2 |
| PA_0_ALT1 | ADC2 | 0 | - | - | - |
| PA_0_ALT2 | ADC3 | 0 | - | - | - |
| PA_1 | ADC1 | 1 | - | D1/A1 | BATT_VIN/3 |
| PA_1_ALT1 | ADC2 | 1 | - | - | - |
| PA_1_ALT2 | ADC3 | 1 | - | - | - |
| PA_2 | ADC1 | 2 | - | D2/A2 | TX1 |
| PA_2_ALT1 | ADC2 | 2 | - | - | - |
| PA_2_ALT2 | ADC3 | 2 | - | - | - |
| PA_3 | ADC1 | 3 | D22 - A6 | D3/A3 | RX1 |
| PA_3_ALT1 | ADC2 | 3 | - | - | - |
| PA_3_ALT2 | ADC3 | 3 | - | - | - |
| PA_4 | ADC1 | 4 | D16 - A0 | D4/A4 | AUD_LRCLK |
| PA_4_ALT1 | ADC2 | 4 | - | - | - |
| PA_5 | ADC1 | 5 | PA_5 | D5/A5 | SCK |
| PA_5_ALT1 | ADC2 | 5 | - | - | - |
| PA_6 | ADC1 | 6 | PA_6 | D6/A6 | CIPO |
| PA_6_ALT1 | ADC2 | 6 | - | - | - |
| PA_7 | ADC1 | 7 | PA_7 | D7/A7 | COPI |
| PA_7_ALT1 | ADC2 | 7 | - | - | - |
| PB_0 | ADC1 | 8 | - | D16/A8 | A1 |
| PB_0_ALT1 | ADC2 | 8 | - | - | - |
| PB_1 | ADC1 | 9 | - | D17/A9 | INT |
| PB_1_ALT1 | ADC2 | 9 | - | - | - |
| PC_0 | ADC1 | 10 | D8 | D32/A10 | D0 |
| PC_0_ALT1 | ADC2 | 10 | - | - | - |
| PC_0_ALT2 | ADC3 | 10 | - | - | - |
| PC_1 | ADC1 | 11 | D13 | D33/A11 | D1 |
| PC_1_ALT1 | ADC2 | 11 | - | - | - |
| PC_1_ALT2 | ADC3 | 11 | - | - | - |
| PC_2 | ADC1 | 12 | PC_2 | D34/A12 | G6 |
| PC_2_ALT1 | ADC2 | 12 | - | - | - |
| PC_2_ALT2 | ADC3 | 12 | - | - | - |
| PC_3 | ADC1 | 13 | PC_3 | D35/A13 | FLASH_CS |
| PC_3_ALT1 | ADC2 | 13 | - | - | - |
| PC_3_ALT2 | ADC3 | 13 | - | - | - |
| PC_4 | ADC1 | 14 | PC_4 | D36/A14 | CS |
| PC_4_ALT1 | ADC2 | 14 | - | - | - |
| PC_5 | ADC1 | 15 | PC_5 | D37/A15 | A0 |
| PC_5_ALT1 | ADC2 | 15 | - | - | - |


[Back to Main Page](../../)