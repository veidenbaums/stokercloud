from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)

# ====== БАЗОВІ НАЛАШТУВАННЯ HTTP API ======
BASE_URL = "https://stokercloud.dk/v2/dataout2"
STATUS_ENDPOINT = "status.php"       # очікуємо JSON зі «поточними» значеннями
OVERVIEW_ENDPOINT = "overview.php"   # (опційно) для агрегованих лічильників/станів, якщо потрібні
UPDATE_ENDPOINT = "updatevalue.php"  # для запису параметрів (write)

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=20)
HTTP_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "homeassistant-stokercloud-write/0.2",
}

# ====== ВИНЯТКИ ======
class NBEApiError(Exception):
    """Базова помилка API."""

class NBEAuthError(NBEApiError):
    """Проблеми аутентифікації/токена."""

class NBENetworkError(NBEApiError):
    """Мережеві/транспортні помилки."""

class NBEInvalidResponse(NBEApiError):
    """Неправильний або порожній JSON з бекенду."""


class NBEApi:
    """Мінімальний async-клієнт до StokerCloud (read + write)."""

    def __init__(
        self,
        serial: str,
        token: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
        base_url: str = BASE_URL,
    ) -> None:
        self._serial = str(serial)
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._session_external = session is not None
        self._session = session or aiohttp.ClientSession(timeout=HTTP_TIMEOUT, headers=HTTP_HEADERS)

    # ---------- публічні методи ----------

    async def async_get_status(self) -> Dict[str, Any]:
        """Повертає нормалізований словник станів під ключі з const.SENSOR_DEFINITIONS / BINARY_SENSOR_DEFINITIONS."""
        raw = await self._get_json(STATUS_ENDPOINT, params={"serial": self._serial})
        if not isinstance(raw, dict):
            raise NBEInvalidResponse("Status response is not a JSON object")

        # (Необов’язково) підтягнути оверв’ю/тотали, якщо доступно
        try:
            overview = await self._get_json(OVERVIEW_ENDPOINT, params={"serial": self._serial})
            if isinstance(overview, dict):
                raw = {**overview, **raw}  # status має пріоритет
        except Exception as ex:  # noqa: BLE001
            _LOGGER.debug("Overview endpoint not used (%s): %s", OVERVIEW_ENDPOINT, ex)

        normalized = self._normalize_payload(raw)
        _LOGGER.debug("Normalized status for %s: %s", self._serial, list(normalized.keys()))
        return normalized

    async def async_set_boiler_temp(self, value: float) -> None:
        """Запис встановленої температури котла."""
        await self._write_value(
            menu="boiler.temp",
            name="boiler.temp",
            value=value,
        )

    async def async_set_hotwater_temp(self, value: float) -> None:
        """Запис встановленої температури ГВП (бойлер ГВП)."""
        await self._write_value(
            menu="hotwater.temp",
            name="hotwater.temp",
            value=value,
        )

    async def async_close(self) -> None:
        """Закрити внутрішню сесію, якщо вона створена тут."""
        if not self._session_external and not self._session.closed:
            await self._session.close()

    # ---------- внутрішні хелпери ----------

    async def _get_json(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        try:
            async with self._session.get(url, params=params) as resp:
                text = await resp.text()
                if resp.status == 401 or resp.status == 403:
                    raise NBEAuthError(f"Auth error {resp.status} on GET {url}")
                if resp.status >= 400:
                    raise NBENetworkError(f"HTTP {resp.status} on GET {url}: {text[:200]}")
                # Деякі ендпоїнти повертають 'application/json; charset=utf-8' або навіть text/plain — парсимо вручну
                try:
                    return json.loads(text)
                except json.JSONDecodeError as je:
                    _LOGGER.debug("JSON decode fail on %s: %s\nPayload: %s", url, je, text[:500])
                    raise NBEInvalidResponse(f"Invalid JSON from {url}") from je
        except asyncio.TimeoutError as te:
            raise NBENetworkError(f"Timeout on GET {url}") from te
        except aiohttp.ClientError as ce:
            raise NBENetworkError(f"Network error on GET {url}: {ce}") from ce

    async def _write_value(self, *, menu: str, name: str, value: float | int | str) -> None:
        """Базовий метод запису через updatevalue.php.

        Параметри згідно з прикладом:
          - menu: наприклад 'boiler.temp'
          - name: як правило так само, 'boiler.temp'
          - token: твій write-token (обов’язковий)
          - value: власне значення (надсилаємо POST-ом)
        """
        if not self._token:
            raise NBEAuthError("Missing token for write operation")

        url = f"{self._base_url}/{UPDATE_ENDPOINT}"
        params = {
            "menu": menu,
            "name": name,
            "token": self._token,
        }
        # значення передаємо як form-data (деякі бекенди не приймають ?value= у GET)
        data = {"value": str(value)}

        try:
            async with self._session.post(url, params=params, data=data) as resp:
                text = await resp.text()
                if resp.status == 401 or resp.status == 403:
                    raise NBEAuthError(f"Auth error {resp.status} on POST {url}")
                if resp.status >= 400:
                    raise NBENetworkError(f"HTTP {resp.status} on POST {url}: {text[:200]}")

                # Очікуємо або JSON, або простий OK/0/1; намагаємось інтерпретувати
                ok = False
                try:
                    payload = json.loads(text)
                    # типові варіанти: {"success": true} / {"status": "ok"} / {"code": 0}
                    ok = (
                        (isinstance(payload, dict) and (
                            payload.get("success") is True
                            or str(payload.get("status", "")).lower() == "ok"
                            or payload.get("code") in (0, "0")
                        )) or False
                    )
                except json.JSONDecodeError:
                    # Трапляється простий "OK" або "1"
                    ok = text.strip().lower() in ("ok", "1", "true", "success")

                if not ok:
                    _LOGGER.warning("Write %s/%s value=%s got non-OK reply: %s", menu, name, value, text[:200])
        except asyncio.TimeoutError as te:
            raise NBENetworkError(f"Timeout on POST {url}") from te
        except aiohttp.ClientError as ce:
            raise NBENetworkError(f"Network error on POST {url}: {ce}") from ce

    def _normalize_payload(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Нормалізує сирі ключі бекенду в «гарні» ключі інтеграції.

        Ми намагаємося закрити найтиповіші варіанти назв від StokerCloud.
        Якщо якийсь ключ інший — легко додати мапінг нижче.
        """
        out: Dict[str, Any] = {}

        def pick(*keys: str, cast=float, default=None):
            for k in keys:
                if k in raw and raw[k] not in (None, ""):
                    try:
                        return cast(raw[k])
                    except Exception:  # noqa: BLE001
                        return raw[k]
            return default

        def pick_str(*keys: str, default=None):
            for k in keys:
                if k in raw and raw[k] not in (None, ""):
                    return str(raw[k])
            return default

        # Температури котла (поточна/встановлена)
        out["boiler_temperature_current"] = pick(
            "boiler_temperature_current", "boiler_temp", "boiler.temperature", "temp_boiler", cast=float
        )
        out["boiler_temperature_requested"] = pick(
            "boiler_temperature_requested", "boiler_temp_set", "boiler.setpoint", "temp_boiler_set", cast=float
        )

        # Ефект/потужність (W)
        out["boiler_kwh"] = pick(
            "boiler_kwh", "boiler_effect", "power", "boiler.power", cast=float
        )

        # Загальне споживання пелет (кг)
        out["consumption_total"] = pick(
            "consumption_total", "pellets_total", "pellets.consumption_total", cast=float
        )

        # Стан (рядок/код стану)
        out["state"] = pick_str("state", "boiler_state", "status", default=None)

        # ГВП поточна/встановлена
        out["hotwater_temperature_current"] = pick(
            "hotwater_temperature_current", "hotwater_temp", "dhw.temperature", cast=float
        )
        out["hotwater_temperature_requested"] = pick(
            "hotwater_temperature_requested", "hotwater_temp_set", "dhw.setpoint", cast=float
        )

        # Бінараки
        # running: 1/0, true/false, "on"/"off"
        running_raw = pick("running", "is_running", "boiler_running", cast=lambda v: v)
        out["running"] = _to_bool(running_raw)

        alarm_raw = pick("alarm", "has_alarm", "alarm_active", cast=lambda v: v)
        out["alarm"] = _to_bool(alarm_raw)

        # Очистимо None-значення, щоб ентіті не «мигали» unknown-ом без потреби
        return {k: v for k, v in out.items() if v is not None}


# ---------- утиліти поза класом ----------

def _to_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        if v == 1 or v is True:
            return True
        if v == 0 or v is False:
            return False
    s = str(v).strip().lower()
    if s in ("1", "true", "on", "yes", "y"):
        return True
    if s in ("0", "false", "off", "no", "n"):
        return False
    return None
