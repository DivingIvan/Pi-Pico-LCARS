from micropython import const

_HUMIDITY_REFERENCE = const(40)
_GAS_LOWER_LIMIT = const(10000)
_GAS_UPPER_LIMIT = const(300000)

def getHumidityScore(current_humidity):
    if (current_humidity >= 38 and current_humidity <= 42):
        humidity_score = 0.25 * 100
    else:
        if (current_humidity < 38):
            humidity_score = 0.25 / _HUMIDITY_REFERENCE * current_humidity * 100
        else:
            humidity_score = ((-0.25 / (100 - _HUMIDITY_REFERENCE) * current_humidity) + 0.416666) * 100
    return humidity_score

def getGasScore(gas_reference):
    gas_score = (0.75 / (_GAS_UPPER_LIMIT - _GAS_LOWER_LIMIT) * gas_reference - (_GAS_LOWER_LIMIT * (0.75 / (_GAS_UPPER_LIMIT - _GAS_LOWER_LIMIT)))) * 100.00
    if (gas_score > 75):
        gas_score = 75
    if (gas_score <  0):
        gas_score = 0
    return gas_score

def getAirQuality(gas_reference, current_humidity):
    humidity_score = getHumidityScore(current_humidity)
    gas_score      = getGasScore(gas_reference)
    air_quality_score = humidity_score + gas_score
    return air_quality_score