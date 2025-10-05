from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, DEVICE_CLASS_TEMPERATURE
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    CONF_SERIAL,
    CONF_NAME,
    DEFAULT_SCAN_INTERVAL,
)
from .api import StokerCloudWriteApi


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]

    async def _async_update():
        return await api.async_get_boiler_temperature()

    coordinator = DataUpdateCoordinator[float | None](
        hass,
        logger=hass.logger,
        name=f"{DOMAIN}_boiler_temp_coordinator",
        update_method_=_async_update,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([BoilerTemperatureSensor(entry, api, coordinator)], True)


class BoilerTemperatureSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Boiler temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = DEVICE_CLASS_TEMPERATURE
    _attr_icon = "mdi:thermometer"

    def __init__(
        self,
        entry: ConfigEntry,
        api: StokerCloudWriteApi,
        coordinator: DataUpdateCoordinator,
    ):
        super().__init__(coordinator)
        self._entry = entry
        self._api = api
        self._serial = entry.data.get(CONF_SERIAL, "unknown")
        self._attr_unique_id = f"{self._serial}_boiler_temperature"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=entry.data.get(CONF_NAME) or f"NBE {self._serial}",
            model="StokerCloud",
        )

    @property
    def native_value(self):
        return self.coordinator.data
