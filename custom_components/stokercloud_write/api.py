from __future__ import annotations


import asyncio
import json
from typing import Any, Tuple


import aiohttp


from .const import API_BASE, API_DATA_PATH, API_WRITE_PATH


class StokerApi:
def __init__(self, serial: str, token: str) -> None:
self._serial = serial
self._token = token


async def async_validate(self) -> Tuple[bool, str | None]:
try:
data = await self.async_fetch()
return (isinstance(data, dict) and len(data) > 0, None)
except Exception as exc: # noqa: BLE001
return (False, str(exc))


async def async_fetch(self) -> dict:
params = {"serial": self._serial, "token": self._token}
url = f"{API_BASE}{API_DATA_PATH}"
timeout = aiohttp.ClientTimeout(total=20)
async with aiohttp.ClientSession(timeout=timeout) as sess:
async with sess.get(url, params=params) as resp:
resp.raise_for_status()
text = await resp.text()
try:
return json.loads(text)
except json.JSONDecodeError:
# Деякі інсталяції повертають single-quoted JSON або trailing commas — спробуємо прибрати сміття
text = text.replace("'", '"').replace(",}\n", "}\n").replace(",]", "]")
return json.loads(text)


async def async_set_boiler_temp(self, value: float) -> None:
params = {
"menu": "boiler.temp",
"name": "boiler.temp",
"value": f"{value}",
"token": self._token,
"serial": self._serial,
}
url = f"{API_BASE}{API_WRITE_PATH}"
timeout = aiohttp.ClientTimeout(total=20)
async with aiohttp.ClientSession(timeout=timeout) as sess:
async with sess.get(url, params=params) as resp: # API приймає GET
resp.raise_for_status()
await resp.text() # ігноруємо тіло; важливий код 200
