from __future__ import annotations

from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

from .const import UPDATE_URL, CONF_TOKEN


class StokerCloudWriteApi:
    """Клієнт для запису значення в StokerCloud."""

    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._session: ClientSession = async_get_clientsession(hass)

    async def async_set_boiler_setpoint(self, value: int) -> bool:
        """Відправити значення температури котла."""
        url = URL(UPDATE_URL).with_query(
            {
                "menu": "boiler.temp",
                "name": "boiler.temp",
                "token": self._entry.data[CONF_TOKEN],
            }
        )
        data = {"value": str(value)}
        try:
            async with self._session.post(str(url), data=data, timeout=15) as resp:
                return resp.status == 200
        except Exception:
            return False
