from micropython import const
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from time import sleep
import gc
import board
import analogio
import digitalio
import busio
import displayio
import adafruit_ili9341
import adafruit_imageload
import adafruit_veml6075
import adafruit_bme680
from ScaleIndicator import scaleIndicator
from adafruit_display_shapes.rect import Rect
from Graph import graph
import AirQuality
import RTC

_PICO = const(0)
_TINY2040 = const(1)

_BOARDTYPE = const(_PICO)

_SEA_LEVEL_NORMAL = const(1013)
_DISPLAY_WIDTH = const(480)
_DISPLAY_HEIGHT = const(320)
#_DISPLAY_WIDTH = const(320)
#_DISPLAY_HEIGHT = const(240)

_PRESSURE_GRAPH_UPDATE_INTERVAL = const(12) # Minutes
_PRESSURE_PLOT_COUNT = const(30)
_PRESSURE_GRAPH_RANGE = const(20)

conversion_factor = 3 * 3.3 / 65535
full_battery = 4.2  # these are our reference voltages for a full/empty battery, in volts
empty_battery = 2.8 # the values could vary by battery size/manufacturer so you might need to adjust them

if (_DISPLAY_WIDTH == 320):
    lcarsBackground = "img/lcars-320x240.bmp"
    font_s = bitmap_font.load_font("fonts/Context_Ultra_Condensed-12.bdf")
    font_m = bitmap_font.load_font("fonts/Context_Ultra_Condensed-16.bdf")
elif (_DISPLAY_WIDTH == 480):
    lcarsBackground = "img/lcars-480x320.bmp"
    font_s = bitmap_font.load_font("fonts/Context_Ultra_Condensed-18.bdf")
    font_m = bitmap_font.load_font("fonts/Context_Ultra_Condensed-24.bdf")

weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

xScaleFactor = _DISPLAY_WIDTH / 320
yScaleFactor = _DISPLAY_HEIGHT / 240

# Release any resources currently in use for the displays
displayio.release_displays()

if _BOARDTYPE == _PICO:
    # Pi Pico
    i2c_scl=board.GP1
    i2c_sda=board.GP0
    spi_clock = board.GP18
    spi_mosi = board.GP19
    spi_miso = board.GP16
    spi_reset = board.GP20
    tft_cs = board.GP17
    tft_dc = board.GP21
    chargingPin = board.GP26
    tft_backlight = board.GP27
    backlightButtonPin = board.GP28
    backlightLEDPin = board.GP15
    powerLEDPin = board.GP14
    voltageMonitor = board.VOLTAGE_MONITOR
elif _BOARDTYPE == _TINY2040:
    #Tiny 2040
    i2c_scl=board.GP1
    i2c_sda=board.GP0
    spi_clock = board.GP6
    spi_mosi = board.GP7
    spi_miso = board.GP4
    spi_reset = board.GP2
    tft_cs = board.GP5
    tft_dc = board.GP3
    chargingPin = board.GP26
    tft_backlight = board.GP27 # ? Not tested
    backlightButtonPin = board.GP28
    backlightLEDPin = board.GP15
    powerLEDPin = board.GP14
    voltageMonitor = board.VOLTAGE_MONITOR

# Set up SPI interface for display
spi = busio.SPI(spi_clock, spi_mosi, spi_miso)

# Set up TFT backlight control
backlight = digitalio.DigitalInOut(tft_backlight)
backlight.switch_to_output()

# Initially switch off the backlight
backlightOn = False
backlight.value = backlightOn

# Set up button to allow backlight to be switched
backlightButton = digitalio.DigitalInOut(backlightButtonPin)
backlightButton.direction = digitalio.Direction.INPUT
backlightButton.pull = digitalio.Pull.UP

# Set up LED to indicate when backlight is off
backlightLED = digitalio.DigitalInOut(backlightLEDPin)
backlightLED.direction = digitalio.Direction.OUTPUT
backlightLED.value = backlightOn

# Set up LED to indicate when power is connected
powerLED = digitalio.DigitalInOut(powerLEDPin)
powerLED.direction = digitalio.Direction.OUTPUT
powerLED.value = False

# Set up SPI display
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=spi_reset)
display = adafruit_ili9341.ILI9341(display_bus, width=_DISPLAY_WIDTH, height=_DISPLAY_HEIGHT)

# Set up I2C devices
i2c = busio.I2C(scl=i2c_scl, sda=i2c_sda)
veml = adafruit_veml6075.VEML6075(i2c, integration_time=100)
#rtc = RTC.RV3028_I2C(i2c, address=0x52)
rtc = RTC.PCF8523_I2C(i2c)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, address=0x76)
bme680.seaLevelhPa = _SEA_LEVEL_NORMAL

# Setup GUI
lcars = displayio.Group()

# Code to set RTC if needed. Code 'save' should be done around 8-10 seconds in advance.
#rtc.datetime = struct_time(2021, 5, 27, 8, 35, 0, 4, -1, -1)

def toggleBacklight():
    # Function to toggle TFT backlight and return whether backlight is on/off.
    global backlightOn
    backlightOn = not backlightOn
    backlight.value = backlightOn
    return backlightOn

def scalePosition(x, y):
    # Simple function to calculate x, y screen positions for different size screens.
    return int(xScaleFactor * x), int(yScaleFactor * y)

# Load display background image
image, palette = adafruit_imageload.load(lcarsBackground, bitmap=displayio.Bitmap, palette=displayio.Palette)
lcars_grid = displayio.TileGrid(image, pixel_shader=palette)
lcars.append(lcars_grid)

# Add various text labels to display
dt = rtc.datetime
datetimeText = label.Label(font=font_m, text=rtc.datetimeString, anchor_point=(0.0, 0.0), color=0xFFFFFF, anchored_position=(scalePosition(45, 2)))
secondsIndicatorX, secondsIndicatorY = scalePosition(155, 2)
secondsIndicator = Rect(secondsIndicatorX, secondsIndicatorY + int((dt.tm_sec // 10) * 3 * yScaleFactor), int(5 * xScaleFactor), int(3 * yScaleFactor) + 2, fill=0xFFFFFF, outline=0xFFFFFF)
voltageText = label.Label(font=font_s, text="{:.2f}v".format(0), anchor_point=(1.0, 0.0), color=0x00FF00, anchored_position=(scalePosition(190, 2)))
batteryText = label.Label(font=font_s, text="{:.0f}%".format(0), anchor_point=(1.0, 0.0), color=0x00FF00, anchored_position=(scalePosition(190, 22)))
weekdayText = label.Label(font=font_s, text=weekdays[dt.tm_wday], anchor_point=(0.0, 0.0), color=0xFFFFFF, anchored_position=(scalePosition(45, 27)))
pressureText = label.Label(font=font_m, text="{:.1f} hPa  {:.1f}%".format(bme680.pressure, bme680.humidity), anchor_point=(1.0, 0.0), color=0xFFFFFF, anchored_position=(scalePosition(210, 47)))
memoryText = label.Label(font=font_s, text="{:d}".format(gc.mem_free()), anchor_point=(1.0, 0.0), color=0xFFFFFF, anchored_position=(scalePosition(35, 5)))

lcars.append(datetimeText)
lcars.append(secondsIndicator)
lcars.append(voltageText)
lcars.append(batteryText)
lcars.append(weekdayText)
lcars.append(pressureText)
lcars.append(memoryText)

# Create scale indicators
uvIndicator = scaleIndicator(display,
    lcars, scalePosition(65, 100),
    (xScaleFactor, yScaleFactor),
    scaleIndicator.LEFT,
    (font_s, font_m),
    "UV", "{:.1f}",
    0x00FF00,
    ([0, 0xFFCC99], [2, 0xFF9966], [5, 0xCC6666]),
    0, 12, 0)
uvaIndicator = scaleIndicator(display,
    lcars, scalePosition(100, 100),
    (xScaleFactor, yScaleFactor),
    scaleIndicator.RIGHT,
    (font_s, font_m),
    "UVA", "{:.1f}",
    0x00FF00,
    ([0, 0xFFCC99], [5, 0xFF9966], [10, 0xCC6666]),
    0, 15, 0)
uvbIndicator = scaleIndicator(display,
    lcars,
    scalePosition(155, 100),
    (xScaleFactor, yScaleFactor),
    scaleIndicator.RIGHT,
    (font_s, font_m),
    "UVB", "{:.1f}",
    0x00FF00,
    ([0, 0xFFCC99], [10, 0xFF9966], [20, 0xCC6666]),
    0, 30, 0)
gasIndicator = scaleIndicator(display,
    lcars,
    scalePosition(235, 100),
    (xScaleFactor, yScaleFactor),
    scaleIndicator.LEFT,
    (font_s, font_m),
    "IAQ", "{:.1f}",
    0x00FF00,
    ([0, 0xFFCC99], [50, 0xFF9900], [100, 0xFF7F00], [150, 0xCC6666]),
    0, 500, 0)
tempIndicator = scaleIndicator(display,
    lcars, scalePosition(270, 100),
    (xScaleFactor, yScaleFactor),
    scaleIndicator.RIGHT,
    (font_s, font_m),
    "°C", "{:.1f}",
    0x00FF00,
    ([-10, 0x9999FF], [10, 0xFFCC99], [25, 0xFF9966], [35, 0xCC6666]),
    -10, 40, 0)

# Add text label to indicate difference between max and min pressures shown on pressure graph
xPressureDatum, yPressureDatum = scalePosition(50, 55)
graphScaleText = label.Label(font=font_s, text="{:.2f}".format(0), anchor_point=(1.0, 0.5), color=0xFFFFFF, anchored_position=(xPressureDatum - int(14 * xScaleFactor), yPressureDatum))
lcars.append(graphScaleText)

# Add pressure graph to display
pressure = bme680.pressure
pressureGraph = graph(lcars, scalePosition(50, 55), (xScaleFactor, yScaleFactor), _PRESSURE_GRAPH_RANGE, [pressure for x in range(_PRESSURE_PLOT_COUNT + 1)])
diffPressure = pressureGraph.updateGraph([pressure for x in range(_PRESSURE_PLOT_COUNT + 1)])
pressureValues = None

# Refresh display
display.show(lcars)
gc.collect()

# Set up ADC to read analog input voltage
adc = analogio.AnalogIn(voltageMonitor)

# Setup pin to detect if external power is being supplied (for battery charging)
charging = digitalio.DigitalInOut(chargingPin)
charging.direction = digitalio.Direction.INPUT

# TFT backlight should currently be off, so switch it on.
toggleBacklight()

# Monitor 'minute' value from RTC for graph updates
lastMinute = dt.tm_min

sleep(0.5)

gc.collect()

while True:
    # If backlight button has been pressed, toggle the TFT backlight
    if backlightButton.value == False:
        toggleBacklight()

    dt = rtc.datetime
    minute = dt.tm_min
    if minute != lastMinute:
        # Minute has ticked over, so check if graph update is required.
        lastMinute = minute
        if minute % _PRESSURE_GRAPH_UPDATE_INTERVAL == 0:
            # Update graph
            gc.collect()
            if pressureValues == None:
                # Pressure values list has not yet been defined, so create and populate it
                pressureValues = [pressure for x in range(_PRESSURE_PLOT_COUNT)]
                # Add extra pressure value for comparison of first point on graph
                pressureValues.append(bme680.pressure)
            else:
                for i in range(_PRESSURE_PLOT_COUNT + 1):
                    if i < _PRESSURE_PLOT_COUNT:
                        pressureValues[i] = pressureValues[i + 1]
                    else:
                        pressureValues[i] = bme680.pressure
            print(pressureValues)

            graphScaleText.text = "{:.2f}".format(pressureGraph.updateGraph(pressureValues))

    uvIndicator.update(veml.uv_index)
    uvaIndicator.update(veml.uva)
    uvbIndicator.update(veml.uvb)
    gasIndicator.update(AirQuality.getAirQuality(bme680.gas, bme680.humidity))
    tempIndicator.update(bme680.temperature)
    secondsIndicator.y = secondsIndicatorY + int((dt.tm_sec // 10) * 3 * yScaleFactor)
    datetimeText.text = rtc.datetimeString
    voltageText.text = "{:.2f}v".format(adc.value * conversion_factor)
    batteryText.text = "{:.0f}%".format(min(100, (100 * ((adc.value * conversion_factor - empty_battery) / (full_battery - empty_battery)))))
    weekdayText.text = weekdays[dt.tm_wday]
    pressureText.text = "{:.1f} hPa  {:.1f}%".format(bme680.pressure, bme680.humidity)
    memoryText.text = "{:d}".format(gc.mem_free())

    # Pulse backlight indicator LED if TFT backlight is off (negative on LED pin will illuminate LED)
    backlightLED.value = backlightOn
    powerLED.value = False
    sleep(0.05)
    backlightLED.value = True
    powerLED.value = True
    sleep(0.45)