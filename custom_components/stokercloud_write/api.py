from __future__ import annotations
from typing import Any, Dict, Optional
from aiohttp import ClientSession
import logging

_LOGGER = logging.getLogger(__name__)

BASE = "https://stokercloud.dk/v2/dataout2"

class StokerCloudClient:
    def __init__(self, session: ClientSession, token: str, phpsessid: Optional[str] = None):
        self._session = session
        self._token = token
        self._cookie = {"PHPSESSID": phpsessid} if phpsessid else None

    async def get_output_settings(self) -> Dict[str, Any]:
        url = f"{BASE}/getoutputsettings.php"
        params = {"token": self._token}
        async with self._session.get(url, params=params, cookies=self._cookie) as resp:
            txt = await resp.text()
            _LOGGER.debug("get_output_settings: status=%s body=%s", resp.status, txt[:500])
            resp.raise_for_status()
            try:
                return await resp.json(content_type=None)
            except Exception:
                return {"raw": txt}

    async def update_value(
        self, *, menu: str, name: str, value: Any, phpsessid: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"{BASE}/updatevalue.php"
        data = {"menu": menu, "name": name, "value": value, "token": self._token}
        cookies = {"PHPSESSID": phpsessid} if phpsessid else self._cookie
        async with self._session.post(url, data=data, cookies=cookies) as resp:
            txt = await resp.text()
            _LOGGER.debug("update_value: status=%s body=%s", resp.status, txt[:500])
            resp.raise_for_status()
            try:
                return await resp.json(content_type=None)
            except Exception:
                return {"status": "ok", "raw": txt}
