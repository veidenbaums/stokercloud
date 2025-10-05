from __future__ import annotations


import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType


from .const import DOMAIN, PLATFORMS
from .coordinator import StokerCoordinator


_LOGGER = logging.getLogger(__name__)


coordinators: dict[str, StokerCoordinator] = {}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
coordinator = StokerCoordinator(hass, entry)
await coordinator.async_config_entry_first_refresh()


coordinators[entry.entry_id] = coordinator


await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


entry.async_on_unload(entry.add_update_listener(_async_update_listener))
return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
if unload_ok:
coordinators.pop(entry.entry_id, None)
return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
await hass.config_entries.async_reload(entry.entry_id)
