import displayio
from adafruit_display_shapes.rect import Rect
from micropython import const

_INCREASE_COLOUR = const(0x00FF00)
_DECREASE_COLOUR = const(0xFF7F00)
_NO_CHANGE_COLOUR = const(0xFFFFFF)

def getOffset(datumValue, value):
    # Calculate the y offset from the graph y datum
    offset = datumValue - value
    return offset

class graph:

    def __init__(self, displayGroup, axesPosition, scaleFactors, yRange, values):
        # Graph takes a list of values, but does not plot the first value.
        # The first value is present only to allow comparison with the following values to show increase or decrease.

        self.xDatum = axesPosition[0]
        self.yDatum = axesPosition[1]
        self.xScaleFactor = scaleFactors[0]
        self.yScaleFactor = scaleFactors[1]
        self.yRange = yRange

        plotCount = len(values) - 1

        # Calculate maximum positive/negative offset either side of median.
        yGraphOffset = int(self.yRange * self.yScaleFactor / 2) + 2

        # Draw vertical and horizontal lines to indicates corner bounds of graph plot
        xPos = self.xDatum - 7
        ulhLine = Rect(xPos, self.yDatum - yGraphOffset, 5, 1, fill=0xFFFFFF, outline=0xFFFFFF)
        ulvLine = Rect(xPos, self.yDatum - yGraphOffset, 1, 5, fill=0xFFFFFF, outline=0xFFFFFF)
        llhLine = Rect(xPos, self.yDatum + yGraphOffset, 5, 1, fill=0xFFFFFF, outline=0xFFFFFF)
        llvLine = Rect(xPos, self.yDatum + yGraphOffset - 5, 1, 5, fill=0xFFFFFF, outline=0xFFFFFF)

        xPos = self.xDatum + plotCount * 2 + 7
        urhLine = Rect(xPos - 5, self.yDatum - yGraphOffset, 5, 1, fill=0xFFFFFF, outline=0xFFFFFF)
        urvLine = Rect(xPos, self.yDatum - yGraphOffset, 1, 5, fill=0xFFFFFF, outline=0xFFFFFF)
        lrhLine = Rect(xPos - 5, self.yDatum + yGraphOffset, 5, 1, fill=0xFFFFFF, outline=0xFFFFFF)
        lrvLine = Rect(xPos, self.yDatum + yGraphOffset - 5, 1, 5, fill=0xFFFFFF, outline=0xFFFFFF)

        displayGroup.append(ulhLine)
        displayGroup.append(ulvLine)
        displayGroup.append(llhLine)
        displayGroup.append(llvLine)
        displayGroup.append(urhLine)
        displayGroup.append(urvLine)
        displayGroup.append(lrhLine)
        displayGroup.append(lrvLine)

        # Define alist of 'points' to be plotted on the graph, and append them to the display group to be displayed.
        self.graph = []
        for i in range(len(values) - 1):
            rect = Rect(self.xDatum + i * 2, self.yDatum, 2, 2, fill=0x000000, outline=0x000000)
            self.graph.append(rect)
            displayGroup.append(rect)

    def updateGraph(self, values):
#        print(values)

        # Calculate median value from historic values
        minValue = min(values)
        maxValue = max(values)
        medianValue = minValue + ((maxValue - minValue) / 2)
        differentialValue = maxValue - minValue
        if differentialValue == 0:
            scaleMultiplier = 1 * self.yScaleFactor
        else:
            scaleMultiplier = (self.yRange / differentialValue) * self.yScaleFactor

#        print("Values - Min = {:.2f} : Max = {:.2f} : Median = {:.2f} : Difference = {:.2f} : Scale Multiplier = {:.2f}".format(minValue, maxValue, medianValue, differentialValue, scaleMultiplier))

        for i in range(len(values) - 1):
            if values[i + 1] > values[i]:
                colour = _INCREASE_COLOUR
            elif values[i + 1] < values[i]:
                colour = _DECREASE_COLOUR
            else:
                colour = _NO_CHANGE_COLOUR
            offset = getOffset(medianValue, values[i + 1])
            self.graph[i].y = int(self.yDatum + (offset * scaleMultiplier))
            self.graph[i].fill = colour
            self.graph[i].outline = colour

        return differentialValue