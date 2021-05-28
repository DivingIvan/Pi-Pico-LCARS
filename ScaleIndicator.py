import adafruit_imageload
import displayio
from adafruit_display_text import label
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.rect import Rect
import math
from micropython import const

_SCALESIZE = const(82)
_DATUMOFFSET = const(115)
_POINTER_SIZE = const(8)

class scaleIndicator:

    LEFT = const(0)
    RIGHT = const(1)

    def __init__(self, display, displayGroup, position, scaleFactors, hand, scaleFonts, scaleLabel, textFormat, colour, scaleColours, minValue, maxValue, value):
        def displayIndicator(x, y, colour):
            if self.hand == scaleIndicator.LEFT:
                shape = Triangle(x, y, x + int(_POINTER_SIZE * self.scaleFactors[0]), y + int(_POINTER_SIZE * self.scaleFactors[1] / 2), x + int(_POINTER_SIZE * self.scaleFactors[0]), y - int(_POINTER_SIZE * self.scaleFactors[1] / 2), fill=colour, outline=colour)
            else:
                shape = Triangle(x, y, x - int(_POINTER_SIZE * self.scaleFactors[0]), y + int(_POINTER_SIZE * self.scaleFactors[1] / 2), x - int(_POINTER_SIZE * self.scaleFactors[0]), y - int(_POINTER_SIZE * self.scaleFactors[1] / 2), fill=colour, outline=colour)
            return shape

        def displayBand(band, x, y):
            colour = self.scaleColours[band][1]
            yMin = self.scaleColours[band][0]
            if band == len(self.scaleColours) - 1:
                yMax = self.maxValue
            else:
                yMax = self.scaleColours[band + 1][0]
            yDiff = yMax - yMin
            if band == 0:
                yPosPrev = y - int(self.minValue * self.yScaleMultiplier)
                if self.minValue < 0:
                    yPosPrev += 1
            else:
                yPosPrev = y - int(self.scaleColours[band][0] * self.yScaleMultiplier)
            yPos =  y - int(yMax * self.yScaleMultiplier)
            ySize = (yPosPrev - yPos) - 1
            if self.hand == scaleIndicator.LEFT:
                shape = Rect(x + int(7 * scaleFactors[0]), yPos, math.ceil(3 * scaleFactors[0]), ySize, fill=colour, outline=colour)
            else:
                shape = Rect(x + 1 + int(15 * scaleFactors[0]), yPos, math.ceil(3 * scaleFactors[0]), ySize, fill=colour, outline=colour)
            return shape

        x = position[0]
        y = position[1]
        if (display.width == 320):
            scaleLeftImage = "img/lcars-scale-left-320x240.bmp"
            scaleRightImage = "img/lcars-scale-right-320x240.bmp"
        elif (display.width == 480):
            scaleLeftImage = "img/lcars-scale-left-480x320.bmp"
            scaleRightImage = "img/lcars-scale-right-480x320.bmp"
        self.hand = hand
        self.minValue = minValue
        self.maxValue = maxValue
        self.scaleColours = scaleColours
        self.scaleFactors = scaleFactors

        self.textFormat = textFormat
        self.colour = colour
        self.yScaleMultiplier = (_SCALESIZE / (maxValue - minValue)) * self.scaleFactors[1]
        self.yZeroDatum = int(y + (_DATUMOFFSET * self.scaleFactors[1]) + (minValue * self.yScaleMultiplier))
        font_s = scaleFonts[0]
        font_m = scaleFonts[1]
        valueString = self.textFormat.format(value)
        if self.hand == scaleIndicator.LEFT:
            self.xAnchor = x + int(3 * self.scaleFactors[0])
            scale, palette = adafruit_imageload.load(scaleLeftImage, bitmap=displayio.Bitmap, palette=displayio.Palette)
            self.shape = displayIndicator(x + int(17 * self.scaleFactors[0]), self.yZeroDatum, self.scaleColours[0][1])
            self.yOffset = self.yZeroDatum - self.shape.y
            self.text = label.Label(font=font_s, text=valueString, anchor_point=(1.0, 0.5), color=0xFFFFFF, anchored_position=(self.xAnchor, self.shape.y + 3))
        else:
            self.xAnchor = x + int(25 * self.scaleFactors[0])
            scale, palette = adafruit_imageload.load(scaleRightImage, bitmap=displayio.Bitmap, palette=displayio.Palette)
            self.shape = displayIndicator(x + int(8 * self.scaleFactors[0]), self.yZeroDatum, self.scaleColours[0][1])
            self.yOffset = self.yZeroDatum - self.shape.y
            self.text = label.Label(font=font_s, text=valueString, anchor_point=(0.0, 0.5), color=0xFFFFFF, anchored_position=(self.xAnchor, self.shape.y + 3))
        grid = displayio.TileGrid(scale, pixel_shader=palette, x = x + int(5 * self.scaleFactors[0]), y = y + int(15 * self.scaleFactors[1]))
        self.scaleLabel = label.Label(font=font_m, text=scaleLabel, color=self.scaleColours[0][1], x = x, y = y)
        displayGroup.append(grid)

        for i in range(len(self.scaleColours)):
            band = displayBand(i, x, self.yZeroDatum)

            displayGroup.append(band)

        displayGroup.append(self.scaleLabel)
        displayGroup.append(self.shape)
        displayGroup.append(self.text)

    def update(self, value):
        if (value < self.minValue):
            value = self.minValue
        elif (value > self.maxValue):
            value = self.maxValue
        self.text.text = self.textFormat.format(value)
        for scaleColour in self.scaleColours:
            if (value >= scaleColour[0]):
                colour = scaleColour[1]
        self.shape.outline = colour
        self.shape.fill = colour
        self.scaleLabel.color = colour
        self.shape.y = math.ceil(self.yZeroDatum - self.yOffset - (value * self.yScaleMultiplier))
        self.text.anchored_position = (self.xAnchor, self.shape.y + 3)