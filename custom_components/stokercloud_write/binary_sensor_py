from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_SERIAL, CONF_NAME, BOILER_SCAN_INTERVAL
from .api import StokerCloudWriteApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]

    async def _upd_running():
        return await api.async_get_boiler_running_from_controller()

    coordinator = DataUpdateCoordinator[bool | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_boiler_running",
        update_method=_upd_running,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([BoilerRunningBinarySensor(entry, coordinator)], True)


class BoilerRunningBinarySensor(CoordinatorEntity[DataUpdateCoordinator[bool | None]], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Boiler running"
    _attr_device_class = BinarySensorDeviceClass.POWER  # або прибери device_class, якщо не хочеш
    _attr_icon = "mdi:power"

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[bool | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_boiler_running"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        # якщо даних нема — сенсор показуватиме unavailable, а не хибний OFF
        return self.coordinator.data is not None

    @property
    def is_on(self) -> bool | None:
        # True → Boiler ON, False → Boiler OFF
        return self.coordinator.data
