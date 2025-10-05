from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    CONF_SERIAL,
    CONF_NAME,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_STEP,
)
from .api import StokerCloudWriteApi


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BoilerSetpointNumber(hass, entry, api)], True)


class BoilerSetpointNumber(RestoreEntity, NumberEntity):
    """Поле ВВОДУ (BOX) для встановлення setpoint котла."""

    _attr_has_entity_name = True
    _attr_name = "Boiler temperature setpoint"
    _attr_icon = "mdi:thermometer-chevron-up"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX  # <- ГОЛОВНЕ: поле вводу замість слайдера
    _attr_native_min_value = DEFAULT_MIN_TEMP
    _attr_native_max_value = DEFAULT_MAX_TEMP
    _attr_native_step = DEFAULT_STEP

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: StokerCloudWriteApi):
        self.hass = hass
        self._entry = entry
        self._api = api
        self._serial = entry.data.get(CONF_SERIAL, "unknown")
        self._attr_unique_id = f"{self._serial}_boiler_temp_setpoint"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=entry.data.get(CONF_NAME) or f"NBE {self._serial}",
            model="StokerCloud",
        )
        self._attr_native_value = None  # відновиться в async_added_to_hass()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = float(last.state)
            except (TypeError, ValueError):
                self._attr_native_value = None
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        # оптимістичний режим: доступний, навіть якщо немає читання стану з хмари
        return True

    async def async_set_native_value(self, value: float) -> None:
        ok = await self._api.async_set_boiler_setpoint(int(round(value)))
        if not ok:
            return
        self._attr_native_value = float(value)
        self.async_write_ha_state()
