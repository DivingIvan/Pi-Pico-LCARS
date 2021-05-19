# Pi-Pico-LCARS

This project is a Raspberry Pi Pico RP2040 based temperature/humidity/atmospheric pressure/air quality/UV monitor with an LCARS style user interface.

(https://github.com/DivingIvan/Pi-Pico-LCARS/blob/main/PXL_20210515_102200687.jpg "LCARS Display")

The original inspiration for this project comes from [@Recantha](https://twitter.com/recantha)'s [PicoPiCorder project](https://github.com/recantha/picopicorder); but with an updated user interface.

The basic components required to implement this project are:-

•	Raspberry Pi Pico RP2040 - https://cpc.farnell.com/raspberry-pi/raspberry-pi-pico/raspberry-pi-pico-rp2040-mcu-board/dp/SC17106

•	TFT display with SPI interface – I used https://thepihut.com/products/adafruit-3-5-tft-320x480-touchscreen-breakout-board-w-microsd-socket

•	BME680 Air Quality, Temperature, Pressure, Humidity sensor - https://shop.pimoroni.com/products/bme680-breakout

•	VEML6075 UVA/B sensor - https://shop.pimoroni.com/products/veml6075-uva-b-sensor-breakout

•	RV3028 RTC - https://shop.pimoroni.com/products/rv3028-real-time-clock-rtc-breakout

•	A momentary SPST push switch. The software has support for an illuminated one, but this is optional. If using an illuminated push switch, you will also require a resistor to limit the LED current.

