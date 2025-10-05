from __future__ import annotations

import logging
from typing import Any

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

# YAML більше не потрібен — просто повертаємо True
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)

    serial = entry.data[CONF_SERIAL_NUMBER]  # збережено як unique_id
    token = entry.data[CONF_TOKEN]
    phpsessid = entry.data.get(CONF_PHPSESSID) or None

    client = StokerCloudClient(session, token, phpsessid)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "serial": serial,
    }

    # зареєструємо сервіс 1 раз (якщо ще не було)
    if f"{DOMAIN}_service_registered" not in hass.data:
        async def _handle_set_value(call: ServiceCall):
            entry_id = call.data.get(ATTR_ENTRY_ID)
            target_entry_id = entry_id or next(iter(hass.data[DOMAIN]), None)
            if not target_entry_id:
                raise ValueError("No stokercloud_write entries available")

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
    if unload_ok and entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
