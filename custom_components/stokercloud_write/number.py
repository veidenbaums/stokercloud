from __future__ import annotations


from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity


from .coordinator import StokerCoordinator
from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
from . import coordinators # noqa
coordinator: StokerCoordinator = coordinators[entry.entry_id]
async_add_entities([BoilerTempNumber(coordinator, entry.entry_id)])


class BoilerTempNumber(CoordinatorEntity[StokerCoordinator], NumberEntity):
_attr_has_entity_name = True
_attr_icon = "mdi:thermostat"
_attr_native_step = 0.5
_attr_mode = "slider"


def __init__(self, coordinator: StokerCoordinator, entry_id: str) -> None:
super().__init__(coordinator)
self._attr_name = "Boiler temperature setpoint"
self._attr_unique_id = f"{entry_id}_boiler_temp_setpoint"
self._attr_native_min_value = 30
self._attr_native_max_value = 90
self._attr_unit_of_measurement = "°C"
self._attr_device_info = {
"identifiers": {(DOMAIN, entry_id)},
"manufacturer": DEVICE_MANUFACTURER,
"model": DEVICE_MODEL,
"name": f"StokerCloud {coordinator.entry.data.get('serial')}",
}


@property
def native_value(self):
# Показуємо поточний setpoint, якщо є в даних; fallback — None
return self.coordinator.data.get("boiler.temp")


async def async_set_native_value(self, value: float) -> None:
await self.coordinator.api.async_set_boiler_temp(value)
await self.coordinator.async_request_refresh()
