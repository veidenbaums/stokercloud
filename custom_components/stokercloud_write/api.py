from __future__ import annotations

from aiohttp import ClientSession
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

from .const import UPDATE_URL, READ_URL, CONF_TOKEN


class StokerCloudWriteApi:
    """Клієнт для взаємодії з StokerCloud."""

    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._session: ClientSession = async_get_clientsession(hass)

    async def async_set_boiler_setpoint(self, value: int) -> bool:
        """Відправити значення температури котла (setpoint)."""
        url = URL(UPDATE_URL).with_query(
            {
                "menu": "boiler.temp",   # ← заміни за потреби
                "name": "boiler.temp",   # ← заміни за потреби
                "token": self._entry.data[CONF_TOKEN],
            }
        )
        data = {"value": str(value)}
        try:
            async with self._session.post(str(url), data=data, timeout=15) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def async_get_boiler_temperature(self) -> float | None:
        """Зчитати поточну температуру котла (в °C)."""
        url = URL(READ_URL).with_query(
            {
                "menu": "boiler.temp",   # ← заміни на фактичний ключ "поточна температура"
                "name": "boiler.temp",   # інколи достатньо лише menu
                "token": self._entry.data[CONF_TOKEN],
            }
        )
        try:
            async with self._session.get(str(url), timeout=15) as resp:
                if resp.status != 200:
                    return None
                # Багато NBE-ендпоінтів повертають або сире число, або JSON з ключем "value"
                ctype = resp.headers.get("Content-Type", "")
                if "application/json" in ctype:
                    data = await resp.json()
                    # шукаємо поширені варіанти
                    for key in ("value", "val", "temp", "temperature"):
                        if key in data:
                            return float(data[key])
                    # або спроба знайти перше числове поле
                    for v in data.values():
                        try:
                            return float(v)
                        except Exception:
                            pass
                    return None
                # якщо текстом — пробуємо спарсити число
                text = (await resp.text()).strip()
                # обрізаємо все зайве (наприклад "65.0\n")
                text = text.splitlines()[0]
                try:
                    return float(text.replace(",", "."))
                except Exception:
                    return None
        except Exception:
            return None
