# Pi-Pico-LCARS

This project is a Raspberry Pi Pico RP2040 based temperature/humidity/atmospheric pressure/air quality/UV monitor with an LCARS style user interface.

![LCARS Display](https://github.com/DivingIvan/Pi-Pico-LCARS/blob/main/PXL_20210515_102200687.jpg "LCARS Display")

The original inspiration for this project comes from [@Recantha](https://twitter.com/recantha)'s [PicoPiCorder project](https://github.com/recantha/picopicorder); but with an updated user interface.

The basic components required to implement this project are:-

•	Raspberry Pi Pico RP2040 - https://cpc.farnell.com/raspberry-pi/raspberry-pi-pico/raspberry-pi-pico-rp2040-mcu-board/dp/SC17106

•	TFT display with SPI interface – I used https://thepihut.com/products/adafruit-3-5-tft-320x480-touchscreen-breakout-board-w-microsd-socket

•	BME680 Air Quality, Temperature, Pressure, Humidity sensor - https://shop.pimoroni.com/products/bme680-breakout

•	VEML6075 UVA/B sensor - https://shop.pimoroni.com/products/veml6075-uva-b-sensor-breakout

•	RV3028 RTC - https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout

# Optional

I have also experimented with a different RTC, the PCF8523 - https://thepihut.com/products/adafruit-pcf8523-real-time-clock-assembled-breakout-board

•	Pico LiPo Shim - https://shop.pimoroni.com/products/pico-lipo-shim (to allow the project to run off a battery).

•	Rechargeable battery. I used a Lithium Ion one - https://shop.pimoroni.com/products/lithium-ion-battery-pack?variant=23417820487

•	One or more momentary SPST push switches, depending on which optional functionality you wish to include. The software has support for illuminated ones, but this is optional. If using illuminated push switches, you will also require appropriate resistors to limit the LED current. I have incorporated 2 illuminated push switches into my implementation; one connected to the Pico reset pin (to allow for soft reset) and one to allow the TFT display backlight to be switched on or off.

•	An optional SPST toggle switch, depending again on which optional functionality you wish to include. I used one in this project, basically to enable/disable the reset push switch. The LED in the reset illuminated push switch indicates when the 'reset' is active.

•	One or more optional LEDs, yet again depending on which optional functionality you might wish to include. You'll also required appropriate resistors to go with them. I used just the one LED for this project (in addition to the illuminated push switches), to indicate when external power is connected.

•	Some sort of enclosure to put everything in.
