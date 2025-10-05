from __future__ import annotations
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DEFINITIONS

@dataclass
class NbeSensorDescription:
    key: str
    name: str
    device_class: str | None
    unit: str | None
    state_class: str | None
    icon: str | None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities: list[NbeSensor] = []
    for d in SENSOR_DEFINITIONS:
        desc = NbeSensorDescription(**d)
        entities.append(NbeSensor(coordinator, entry, desc))
    async_add_entities(entities)

class NbeSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, desc: NbeSensorDescription):
        super().__init__(coordinator)
        self._entry = entry
        self.entity_id = None
        self._desc = desc
        self._attr_name = desc.name
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        if desc.device_class:
            self._attr_device_class = getattr(SensorDeviceClass, desc.device_class, None)
        if desc.state_class:
            self._attr_state_class = getattr(SensorStateClass, desc.state_class, None)
        self._attr_native_unit_of_measurement = desc.unit
        if desc.icon:
            self._attr_icon = desc.icon

    @property
    def native_value(self):
        return self.coordinator.data.get(self._desc.key)

    @property
    def device_info(self):
        # Обов'язково те саме, що й у твоєму number entity
        return {
            "identifiers": {(DOMAIN, self._entry.data["serial"])},
            "manufacturer": "NBE / StokerCloud",
            "name": f"StokerCloud {self._entry.data['serial']}",
            "model": "Bio/Scotte",
        }
