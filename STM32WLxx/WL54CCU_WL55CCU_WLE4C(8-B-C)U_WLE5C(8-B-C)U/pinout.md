---
layout: default
grand_parent: STM32 Family Pinout
parent: STM32WLxx Family Pinout
title: WL54CCU_WL55CCU_WLE4C(8-B-C)U_WLE5C(8-B-C)U Pinout
has_children: false
---

[Home](../../index) / [STM32WLxx](../index) / WL54CCU_WL55CCU_WLE4C(8-B-C)U_WLE5C(8-B-C)U

## PWM Timer Pins

| Pin | PWM Timer | Channel | generic | GENERIC_NODE_SE_TTI | RAK3172_MODULE |
| --- | --- | --- | --- | --- | --- |
| PA_0 | TIM2 | 1 | D0 | D8/FE_CTRL1 | D0 |
| PA_1 | TIM2 | 2 | D1 | D9/FE_CTRL2 | D1 |
| PA_2 | TIM2 | 3 | D2 | D2/TX | D2     - USART2/LPUART1 TX |
| PA_3 | TIM2 | 4 | D3 | D3/RX | D3     - USART2/LPUART1 RX |
| PA_5 | TIM2 | 1 | D5 | D11/SCK1 | D5     - SPI_SCK |
| PA_6 | TIM16 | 1 | D6 | D12/MISO | D6     - SPI_MISO |
| PA_7 | TIM1 | 1N | D7 | D13/MOSI | D7     - SPI_MOSI |
| PA_7_ALT1 | TIM17 | 1 | - | - | - |
| PA_8 | TIM1 | 1 | D8 | D14/ACCEL_INT2 | D8 |
| PA_9 | TIM1 | 2 | D9 | D15/SCL1 | D9 |
| PA_10 | TIM1 | 3 | D10/A0 | D16/SDA1 | D10/A3 |
| PA_11 | TIM1 | 4 | D11/A1 | D4/SDA2/A1 | D11/A7 - I2C_SDA |
| PA_15 | TIM2 | 1 | D15/A5 | D1/BUZZER | D15/A4 |
| PB_3 | TIM2 | 2 | D18/A7 | D0/USR_BTN/SWO/RTS | D17/A0 |
| PB_6 | TIM16 | 1N | D21 | D21/LED_GREEN | D20    - USART1_TX |
| PB_7 | TIM17 | 1N | D22 | D22/LED_BLUE | D21    - USAR1_RX |
| PB_8 | TIM1 | 2N | D23 | D23/FE_CTRL3 | D22 |
| PB_8_ALT1 | TIM16 | 1 | - | - | - |


## ADC Pins

| Pin | ADC | Channel | generic | GENERIC_NODE_SE_TTI | RAK3172_MODULE |
| --- | --- | --- | --- | --- | --- |
| PA_10 | ADC1 | 6 | D10/A0 | D16/SDA1 | D10/A3 |
| PA_11 | ADC1 | 7 | D11/A1 | D4/SDA2/A1 | D11/A7 - I2C_SDA |
| PA_12 | ADC1 | 8 | D12/A2 | D5/SCL2/A2 | D12/A8 - I2C_SCL |
| PA_13 | ADC1 | 9 | D13/A3 | D6/A3/SWDIO | D13/A5 - SWDIO |
| PA_14 | ADC1 | 10 | D14/A4 | D7/A4/SWCLK | D14/A6 - SWCLK |
| PA_15 | ADC1 | 11 | D15/A5 | D1/BUZZER | D15/A4 |
| PB_2 | ADC1 | 4 | D17/A6 | D18/VABAT_ADC/A0 | D16/A2 |
| PB_3 | ADC1 | 2 | D18/A7 | D0/USR_BTN/SWO/RTS | D17/A0 |
| PB_4 | ADC1 | 3 | D19/A8 | D19/VBAT_READ_EN | D18/A1 |


[Back to Main Page](../../index)