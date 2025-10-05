from __future__ import annotations
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL, CONF_SERIAL

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    serial = data["serial"]

    # Додаємо одну керовану number-сутність для прикладу
    entities = [BoilerTempNumber(api=api, serial=serial)]
    async_add_entities(entities, update_before_add=False)

class BoilerTempNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Boiler temperature setpoint"
    _attr_icon = "mdi:thermometer"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 30.0
    _attr_native_max_value = 90.0
    _attr_native_step = 0.5

    def __init__(self, api, serial: str) -> None:
        self._api = api
        self._serial = serial
        self._value: float | None = None
        self._attr_unique_id = f"{serial}_boiler_temp_setpoint"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "name": f"NBE {serial}",
            "configuration_url": "https://stokercloud.dk",
        }

    @property
    def native_value(self) -> float | None:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        # Підставляй свої реальні 'menu'/'name'
        await self._api.async_set_value(menu="boiler.temp", name="boiler.temp", value=value)
        self._value = value
        self.async_write_ha_state()
