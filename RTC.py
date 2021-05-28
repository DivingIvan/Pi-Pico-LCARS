import adafruit_pcf8523
from time import sleep, struct_time, monotonic
from micropython import const

#    I2C ADDRESS/BITS/SETTINGS
#    -----------------------------------------------------------------------

_RV3028_EEPROM_BACKUP_ADDR = const(0x37)
_RV3028_RTC_BSM_MODE_LSM = const(0x03)

_RV3028_DATETIME_REG = const(0x00)
_RV3028_SECOND_REG = const(0x00)
_RV3028_MINUTE_REG = const(0x01)
_RV3028_HOUR_REG = const(0x02)
_RV3028_WEEKDAY_REG = const(0x03)
_RV3028_DATE_REG = const(0x04)
_RV3028_MONTH_REG = const(0x05)
_RV3028_YEAR_REG = const(0x06)

def _decodeBCDVal(byteVal):
    return ((byteVal & 0xf0) >> 4) * 10 + (byteVal & 0x0f);

def _encodeBCDVal(val):
    upper = (int)(val / 10) << 4
    lower = val % 10
    return upper | lower

class RV3028:
    def setRTCBatterySwitchoverMode(self, mode):
        ctrl = self._read_byte(_RV3028_EEPROM_BACKUP_ADDR)
        sleep(0.005)
        ctrl = ctrl | (mode << 2)
        self._write(_RV3028_EEPROM_BACKUP_ADDR, [ctrl])
        ctrl = self._read_byte(_RV3028_EEPROM_BACKUP_ADDR)
        return 0

    def __init__(self, *, refresh_rate=10):
        self.setRTCBatterySwitchoverMode(_RV3028_RTC_BSM_MODE_LSM)
        self._last_reading = 0
        self._min_refresh_time = 1 / refresh_rate

    @property
    def datetimeString(self):
        self._perform_reading()
        return "{:02d}/{:02d}/{:04d} {:02d}:{:02d}".format(self._date, self._month, self._year, self._hour, self._minute)

    @property
    def datetime(self):
        self._perform_reading()
        return struct_time(self._year, self._month, self._date, self._hour, self._minute, self._second, self._weekday, -1, -1)

    @datetime.setter
    def datetime(self, value):
        self.setRTCDate(value.tm_mday, value.tm_mon, value.tm_year)
        self.setRTCTime(value.tm_hour, value.tm_min, value.tm_sec)
        self.setRTCWeekday(value.tm_wday)

    def validateTime(self, hour, minute, second):
        if (hour < 0 or hour > 23 or
            minute < 0 or minute > 59 or
            second < 0 or second > 59):
            return -1
        else:
            return 0

    def validateDate(self, date, month, year):
        year = year - 2000
        if (year < 0 or year > 99 or
            month < 1 or month > 12 or
            date < 1):
            return -1
        else:
            maxDays = 0
            if (month == 4 or month == 6 or month == 9 or month == 11):
                maxDays = 30
            elif (month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12):
                maxDays = 31
            elif (month == 2):
                if (year % 4 == 0):
                    maxDays = 29
                else:
                    maxDays = 28

        if (date > maxDays):
            return -1
        else:
            return 0

    def validateWeekday(self, weekday):
        if (weekday < 0 or weekday > 6):
            return -1
        else:
            return 0

    def setRTCTime(self, hour, minute, second):
        if (self.validateTime(hour, minute, second) != 0):
            return -1
        elif (self.setRTCBatterySwitchoverMode(_RV3028_RTC_BSM_MODE_LSM) != 0):
            return -1
        else:
            self._write(_RV3028_HOUR_REG, [_encodeBCDVal(hour)])
            self._write(_RV3028_MINUTE_REG, [_encodeBCDVal(minute)])
            self._write(_RV3028_SECOND_REG, [_encodeBCDVal(second)])
            return 0;

    def setRTCDate(self, date, month, year):
        if (self.validateDate(date, month, year) != 0):
            return -1
        elif (self.setRTCBatterySwitchoverMode(_RV3028_RTC_BSM_MODE_LSM) != 0):
            return -1
        else:
            self._write(_RV3028_DATE_REG, [_encodeBCDVal(date)])
            self._write(_RV3028_MONTH_REG, [_encodeBCDVal(month)])
            self._write(_RV3028_YEAR_REG, [_encodeBCDVal(year - 2000)])
            return 0;

    def setRTCWeekday(self, weekday):
        if (self.validateWeekday(weekday) != 0):
            return -1
        elif (self.setRTCBatterySwitchoverMode(_RV3028_RTC_BSM_MODE_LSM) != 0):
            return -1
        else:
            self._write(_RV3028_WEEKDAY_REG, [weekday])
            return 0;

    def _perform_reading(self):
        """Perform a single-shot reading from the sensor and fill internal data structure for
        calculations"""
        if monotonic() - self._last_reading < self._min_refresh_time:
            return

        new_data = False
        while not new_data:
            data = self._read(_RV3028_DATETIME_REG, 7)
            new_data = data[4] & 0xFF != 0
            sleep(0.005)
        self._last_reading = monotonic()

        self._second = _decodeBCDVal(data[0])
        self._minute = _decodeBCDVal(data[1])
        self._hour = _decodeBCDVal(data[2])
        self._weekday = data[3]
        self._date = _decodeBCDVal(data[4])
        self._month = _decodeBCDVal(data[5])
        self._year = _decodeBCDVal(data[6]) + 2000

    def _read_byte(self, register):
        """Read a byte register value and return it"""
        return self._read(register, 1)[0]

    def _read(self, register, length):
        raise NotImplementedError()

    def _write(self, register, values):
        raise NotImplementedError()

class RV3028_I2C(RV3028):

    def __init__(self, i2c, address=0x77, debug=False, *, refresh_rate=10):
        """Initialize the I2C device at the 'address' given"""
        from adafruit_bus_device import (  # pylint: disable=import-outside-toplevel
            i2c_device,
        )

        self._i2c = i2c_device.I2CDevice(i2c, address)
        self._debug = debug
        super().__init__(refresh_rate=refresh_rate)

    def _read(self, register, length):
        """Returns an array of 'length' bytes from the 'register'"""
        with self._i2c as i2c:
            i2c.write(bytes([register & 0xFF]))
            result = bytearray(length)
            i2c.readinto(result)
            if self._debug:
                print("\t$%02X => %s" % (register, [hex(i) for i in result]))
            return result

    def _write(self, register, values):
        """Writes an array of 'length' bytes to the 'register'"""
        with self._i2c as i2c:
            buffer = bytearray(2 * len(values))
            for i, value in enumerate(values):
                buffer[2 * i] = register + i
                buffer[2 * i + 1] = value
            i2c.write(buffer)
            if self._debug:
                print("\t$%02X <= %s" % (values[0], [hex(i) for i in values[1:]]))

# Create a subclass for the PCF8523 RTC
class PCF8523_I2C(adafruit_pcf8523.PCF8523):
    def __init__(self, i2c):
        super().__init__(i2c)

    @property
    def datetimeString(self):
        dt = self.datetime
        return "{:02d}/{:02d}/{:04d} {:02d}:{:02d}".format(dt.tm_mday, dt.tm_mon, dt.tm_year, dt.tm_hour, dt.tm_min)