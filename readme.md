# Maker Badge NFC Addon

![preview](doc/out.gif)

[Maker Badge](https://github.com/dronecz/maker_badge) by @dronecz is basicaly wareble device but there is no BLE support (ESP32-S2 does not have one) so no easy way how to communicat with your mobile phone. Cabel is not convinient and WiFi is anoing to setup. Hoever there is one communication oprtion even easier to use then BLE - **NFC**! 


## Introduction

This project utilize NXP [NT3H2211](https://www.nxp.com/products/rfid-nfc/nfc-hf/connected-nfc-tags/ntag-ic-plus-2k-nfc-forum-type-2-tag-with-ic-interface:NTAG_I2C) (it is basically I2C EEPROM memory on one side and NFC tag on the other). It behaves as normal passive NFC Tag and you can use **any mobile application** (like NFC Tools, NXP Tag Writer, …) to write textutal NDEF record to it and it will show up on display.

Text message should be in form: `first line, second line, third line`


## HW

<img src="doc/tags.jpg" width="300" valign="right" />

There are several options, NXP NT3H2211 is not option, there is also ST25DV04K from ST Micro and others.

- NXP NT3H2211
    - [My PCB](https://twitter.com/horcicaa/status/1384975779650543619) (look into HW folder)
    - [NFC TAG from Hardwario](https://obchod.hardwario.cz/nfc-tag/)
- ST25DV04K
    - [ANT7-T-ST25DV04K Reference board for the ST25DV04K](https://www.st.com/en/evaluation-tools/ant7-t-st25dv04k.html)
    - [Adafruit ST25DV16K I2C RFID EEPROM Breakout](https://www.adafruit.com/product/4701)

Note: ST25DV04K has different memory layout then NT3H2211 and it is not supported in current version. 

## Theory of opperation

SW is written in circuitpython. After power up it will read tag memory via i2c and try to find NDEF text message there. 
If there is one it will get text out and show it on display.
Then it will set alarm on field detect pin of NT3H2211 and go to deep sleep (when phone with active NFC is in proximity it will wake UP the badge).

## Future improvements

- Support other tags not only NT3H2211
- Support NDEF format for business card
- Allow to lock tag (e.g. via menu on display), especially useful when business card format will be supported. So other can scan your badge to get contact information but cannot change it.
