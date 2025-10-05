from __future__ import annotations
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, PLATFORMS, CONF_SERIAL, CONF_TOKEN

type HassData = dict[str, dict]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    serial = entry.data[CONF_SERIAL]
    token = entry.data[CONF_TOKEN]

    # Простіший “клієнт” — заміни на твій реальний HTTP-клієнт
    api = StokerCloudApi(token=token, serial=serial)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"api": api, "serial": serial, "token": token}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


# ---- простенький клієнт (для прикладу) ----
import asyncio
import aiohttp

class StokerCloudApi:
    def __init__(self, token: str, serial: str) -> None:
        self._token = token
        self._serial = serial
        self._session: aiohttp.ClientSession | None = None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_set_value(self, menu: str, name: str, value: float | int | str) -> None:
        # приклад ендпоїнта — підстав свій
        url = "https://stokercloud.dk/v2/dataout2/updatevalue.php"
        payload = {"menu": menu, "name": name, "value": value, "token": self._token}
        sess = await self._session_get()
        async with sess.get(url, params=payload, timeout=20) as resp:
            text = await resp.text()
            if resp.status != 200 or "OK" not in text.upper():
                raise RuntimeError(f"Update failed: {resp.status} {text}")

    async def async_close(self):
        if self._session and not self._session.closed:
            await self._session.close()
