from __future__ import annotations


def _include_key(key: str) -> bool:
if key in SENSOR_EXCLUDE_EXACT:
return False
if any(key.startswith(p) for p in SENSOR_EXCLUDE_PREFIXES):
return False
# пропустимо явно керовану нами "boiler.temp" як сенсор? — ні, залишимо й сенсор і number
return True




def _pretty_name(key: str) -> str:
parts = key.split(".")
parts = [p.replace("_", " ").capitalize() for p in parts]
return " / ".join(parts)




def _guess_unit_and_class(key: str, value: Any):
k = key.lower()
text = k.split(".")[-1]


if any(s in text for s in ("temp", "temperature")):
return (TEMP_CELSIUS, SensorDeviceClass.TEMPERATURE)
if any(s in text for s in ("pressure",)):
return (UnitOfPressure.BAR, SensorDeviceClass.PRESSURE)
if any(s in text for s in ("power",)):
return (UnitOfPower.KILO_WATT, SensorDeviceClass.POWER)
if any(s in text for s in ("energy", "kwh")):
return (UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY)
if any(s in text for s in ("pct", "percent", "%")):
return (PERCENTAGE, None)
if re.search(r"rpm$", text):
return (REVOLUTIONS_PER_MINUTE, None)


return (None, None)




class StokerDynamicSensor(CoordinatorEntity[StokerCoordinator], SensorEntity):
_attr_has_entity_name = True


def __init__(self, coordinator: StokerCoordinator, entry_id: str, key: str, name: str, unit, device_class) -> None:
super().__init__(coordinator)
self._key = key
self._attr_unique_id = f"{entry_id}_{key}"
self._attr_name = name
self._attr_native_unit_of_measurement = unit
self._attr_device_class = device_class
self._attr_device_info = {
"identifiers": {(DOMAIN, entry_id)},
"manufacturer": DEVICE_MANUFACTURER,
"model": DEVICE_MODEL,
"name": f"StokerCloud {coordinator.entry.data.get('serial')}",
}


@property
def native_value(self):
return self.coordinator.data.get(self._key)
