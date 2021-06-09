# Pi-Pico-LCARS

This project is a Raspberry Pi Pico RP2040 based temperature/humidity/atmospheric pressure/air quality/UV monitor with an LCARS style user interface.

# IMPORTANT NOTE

**The boot.py script file is an optional file. This Python script will run on every boot. When executed, the root filesystem will be mounted so that CircuitPython can write to it. This script file allows files to be saved to the flash drive through CircuitPython code. The Pi Pico LCARS code will save a list of historic atmospheric pressure readings in order to allow the pressure trend graph to be drawn. This can only be done if the filesystem is writable. If you do not wish to save these readings, this boot.py script file is not required.**

**HOWEVER - Allowing the CircuitPython code to write to the filesystem means that USB write access will be disabled. Thus, you will no longer be able to edit the code using the CircuitPython editor or by other means. Furthermore, you will be unable to delete or rename the boot.py file using file manager.**

**The boot.py file contains instructions in the code comments as to how to regain access to the filesystem through USB.**

![LCARS](https://github.com/DivingIvan/Pi-Pico-LCARS/blob/main/PXL_20210609_073804950.jpg "LCARS")
![LCARS Display](https://github.com/DivingIvan/Pi-Pico-LCARS/blob/main/PXL_20210609_073912946.jpg "LCARS Display")

The original inspiration for this project comes from [@Recantha](https://twitter.com/recantha)'s [PicoPiCorder project](https://github.com/recantha/picopicorder); but with an updated user interface.

Note: In the early stages of this project I also tried running on a Pimoroni Tiny 2040 (https://shop.pimoroni.com/products/tiny-2040), and some of the code from this is still present. However, as I added more features I eventually ran out of usable GPIO pins.

The basic components required to implement this project are:-

•	Raspberry Pi Pico RP2040 - https://cpc.farnell.com/raspberry-pi/raspberry-pi-pico/raspberry-pi-pico-rp2040-mcu-board/dp/SC17106

•	TFT display with SPI interface – I used https://thepihut.com/products/adafruit-3-5-tft-320x480-touchscreen-breakout-board-w-microsd-socket

•	BME680 Air Quality, Temperature, Pressure, Humidity sensor - https://shop.pimoroni.com/products/bme680-breakout

•	VEML6075 UVA/B sensor - https://shop.pimoroni.com/products/veml6075-uva-b-sensor-breakout

•	RV3028 RTC - https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout

I have also experimented with 2 other Real Time Clocks, and the code includes the necessary libraries.

•	PCF8523 - https://thepihut.com/products/adafruit-pcf8523-real-time-clock-assembled-breakout-board

•	DS3231 - https://thepihut.com/products/adafruit-ds3231-precision-rtc-breakout

•	Various jumper wires/signal wire/breadboard/prototyping board/PCB pins and sockets/solder, etc.

# Optional

•	Pico LiPo Shim - https://shop.pimoroni.com/products/pico-lipo-shim (to allow the project to run off a battery).

•	Rechargeable battery. I used a Lithium Ion one - https://shop.pimoroni.com/products/lithium-ion-battery-pack?variant=23417820487

•	Panel mount micro USB extension lead, to allow external connection if the project is going inside an enclosure - https://shop.pimoroni.com/products/right-angle-panel-mount-extension-cables-25cm?variant=32013609631827

•	One or more momentary SPST push switches, depending on which optional functionality you wish to include. The software has support for illuminated ones, but this is optional. If using illuminated push switches, you will also require appropriate resistors to limit the LED current. I have incorporated 2 illuminated push switches into my implementation; one connected to the Pico reset pin (to allow for soft reset) and one to allow the TFT display backlight to be switched on or off.

•	An optional SPST toggle switch, depending again on which optional functionality you wish to include. I used one in this project, basically to enable/disable the reset push switch. The LED in the reset illuminated push switch indicates when the 'reset' is active.

•	One or more optional LEDs, yet again depending on which optional functionality you might wish to include. You'll also require appropriate resistors to go with them. I used just the one LED for this project (in addition to the illuminated push switches), to indicate when external power is connected.

•	Some sort of enclosure to put everything in.
