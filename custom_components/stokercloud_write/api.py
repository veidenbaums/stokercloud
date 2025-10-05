from __future__ import annotations
from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL
from .const import (
    UPDATE_URL, READ_URL, CONF_TOKEN,
    MISC_START_NAME, MISC_STOP_NAME, MISC_CMD_VALUE,
)

class StokerCloudWriteApi:
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._session: ClientSession = async_get_clientsession(hass)

    async def async_set_boiler_setpoint(self, value: int) -> bool:
        url = URL(UPDATE_URL).with_query({
            "menu": "boiler.temp",
            "name": "boiler.temp",
            "token": self._entry.data[CONF_TOKEN],
        })
        data = {"value": str(value)}
        try:
            async with self._session.post(str(url), data=data, timeout=15) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def async_get_boiler_temperature(self) -> float | None:
        url = URL(READ_URL).with_query({
            "menu": "boiler_temperature_current",
            "name": "boiler_temperature_current",
            "token": self._entry.data[CONF_TOKEN],
        })
        try:
            async with self._session.get(str(url), timeout=15) as resp:
                if resp.status != 200:
                    return None
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" in ctype:
                    data = await resp.json()
                    for key in ("value", "val", "temp", "temperature"):
                        if key in data:
                            return float(str(data[key]).replace(",", "."))
                    for v in data.values():
                        try:
                            return float(str(v).replace(",", "."))
                        except Exception:
                            pass
                    return None
                text = (await resp.text()).strip().splitlines()[0]
                return float(text.replace(",", "."))
        except Exception:
            return None

    async def async_set_power(self, turn_on: bool) -> bool:
        """
        Увімкнути -> misc.start=1
        Вимкнути  -> misc.stop=1
        """
        name = MISC_START_NAME if turn_on else MISC_STOP_NAME
        url = URL(UPDATE_URL).with_query({
            "name": name,
            "token": self._entry.data[CONF_TOKEN],
        })
        data = {"value": MISC_CMD_VALUE}
        try:
            async with self._session.post(str(url), data=data, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False
