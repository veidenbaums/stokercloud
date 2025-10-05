from __future__ import annotations

from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPower,
    UnitOfMass,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

# ====== БАЗОВІ КОНСТАНТИ ======
DOMAIN = "stokercloud_write"
DEFAULT_SCAN_INTERVAL = 30  # сек

MANUFACTURER = "NBE / StokerCloud"
MODEL = "Bio/Scotte"

# Які платформи інтеграція піднімає (для довідки всередині проекту)
PLATFORMS = ["sensor", "binary_sensor", "number", "water_heater"]

# ====== СЕНСОРИ (read-only) ======
# Всі ключі тут відповідають client_key з оригінальної інтеграції:
#   - boiler_temperature_current
#   - boiler_temperature_requested
#   - boiler_kwh
#   - consumption_total
#   - state
#   - hotwater_temperature_current
#   - hotwater_temperature_requested
#
# Якщо в coordinator.data значення — об’єкт типу Value(...),
# платформа sensor.native_unit_of_measurement все одно виставить коректну одиницю,
# але тут фіксуємо очікувані одиниці для явності.

SENSOR_DEFINITIONS: list[dict] = [
    {
        "key": "boiler_temperature_current",
        "name": "Boiler Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
    {
        "key": "boiler_temperature_requested",
        "name": "Boiler Temperature Requested",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
    {
        # У материнській інтеграції ключ називається "boiler_kwh" і повертає Value з Unit.KWH,
        # але відображається як потужність (Power). Тож лишаємо клас POWER і ватти.
        "key": "boiler_kwh",
        "name": "Boiler Effect",
        "device_class": SensorDeviceClass.POWER,
        "unit": UnitOfPower.WATT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
    {
        "key": "consumption_total",
        "name": "Total Consumption",
        "device_class": None,
        "unit": UnitOfMass.KILOGRAMS,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": None,
    },
    {
        "key": "state",
        "name": "State",
        "device_class": None,
        "unit": None,
        "state_class": None,
        "icon": None,
    },
    {
        "key": "hotwater_temperature_current",
        "name": "Current Water Heater Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
    {
        "key": "hotwater_temperature_requested",
        "name": "Requested Water Heater Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": None,
    },
]

# ====== БІНАРНІ СЕНСОРИ ======
# running → чи працює котел зараз; alarm → наявність тривоги
BINARY_SENSOR_DEFINITIONS: list[dict] = [
    {
        "key": "running",
        "name": "Running",
        "device_class": BinarySensorDeviceClass.POWER,  # ON = працює
        "icon": None,
    },
    {
        "key": "alarm",
        "name": "Alarm",
        "device_class": BinarySensorDeviceClass.PROBLEM,  # ON = є проблема
        "icon": None,
    },
]

# ====== ДОП. КОНСТАНТИ ДЛЯ device_info (щоб number/sensor/binary_sensor зібрались в один девайс) ======
def device_info_for_serial(serial: str) -> dict:
    return {
        "identifiers": {(DOMAIN, serial)},
        "manufacturer": MANUFACTURER,
        "name": f"StokerCloud {serial}",
        "model": MODEL,
    }
