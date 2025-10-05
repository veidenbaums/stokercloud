from __future__ import annotations
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, PLATFORMS,
    CONF_SERIAL_NUMBER, CONF_TOKEN, CONF_PHPSESSID,
    ATTR_MENU, ATTR_NAME, ATTR_VALUE, ATTR_PHPSESSID, ATTR_ENTRY_ID,
)
from .api import StokerCloudClient

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    # YAML не використовуємо
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    serial = entry.data[CONF_SERIAL_NUMBER]
    token = entry.data[CONF_TOKEN]
    phpsessid = entry.data.get(CONF_PHPSESSID) or None

    client = StokerCloudClient(session, token, phpsessid)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"client": client, "serial": serial}

    if f"{DOMAIN}_service_registered" not in hass.data:
        async def _handle_set_value(call: ServiceCall):
            target_entry_id = call.data.get(ATTR_ENTRY_ID) or next(iter(hass.data[DOMAIN]), None)
            data = hass.data[DOMAIN][target_entry_id]
            client: StokerCloudClient = data["client"]
            await client.update_value(
                menu=call.data[ATTR_MENU],
                name=call.data[ATTR_NAME],
                value=call.data[ATTR_VALUE],
                phpsessid=call.data.get(ATTR_PHPSESSID),
            )
        hass.services.async_register(DOMAIN, "set_value", _handle_set_value)
        hass.data[f"{DOMAIN}_service_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("StokerCloud Write set up for serial=%s", serial)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
