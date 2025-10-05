from __future__ import annotations
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_SERIAL, CONF_NAME
from .api import StokerCloudWriteApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BoilerPowerSwitch(entry, api)], True)


class BoilerPowerSwitch(RestoreEntity, SwitchEntity):
    """Керування котлом через misc.start/misc.stop."""

    _attr_has_entity_name = True
    _attr_name = "Boiler power"
    _attr_icon = "mdi:power"
    # Переконуємось, що за замовчуванням ентіті НЕ відключається
    _attr_entity_registry_enabled_default = True

    def __init__(self, entry: ConfigEntry, api: StokerCloudWriteApi):
        self._entry = entry
        self._api = api
        self._serial = entry.data.get(CONF_SERIAL, "unknown")
        self._attr_unique_id = f"{self._serial}_boiler_power"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=entry.data.get(CONF_NAME) or f"NBE {self._serial}",
            model="StokerCloud",
        )
        self._attr_is_on = None  # стане True/False після відновлення або першої дії

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is not None:
            self._attr_is_on = (last.state == "on")
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        # Оптимістичний режим — керування працює без читання стану з хмари
        return True

    async def async_turn_on(self, **kwargs) -> None:
        ok = await self._api.async_set_power(True)   # misc.start=1
        if ok:
            self._attr_is_on = True
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Failed to turn ON boiler (misc.start=1)")

    async def async_turn_off(self, **kwargs) -> None:
        ok = await self._api.async_set_power(False)  # misc.stop=1
        if ok:
            self._attr_is_on = False
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Failed to turn OFF boiler (misc.stop=1)")
