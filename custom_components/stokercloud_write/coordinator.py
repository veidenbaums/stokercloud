from __future__ import annotations


from datetime import timedelta
import logging
from typing import Any


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from .const import CONF_SCAN_INTERVAL, CONF_SERIAL, CONF_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN
from .api import StokerApi


_LOGGER = logging.getLogger(__name__)


class StokerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
self.entry = entry
self.api = StokerApi(serial=entry.data[CONF_SERIAL], token=entry.data[CONF_TOKEN])
interval = timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds())))
super().__init__(
hass,
_LOGGER,
name=f"StokerCloud {entry.data[CONF_SERIAL]}",
update_interval=interval,
)


async def _async_update_data(self) -> dict[str, Any]:
try:
data = await self.api.async_fetch()
# Очікуємо, що дані приходять як dict; вкладені частини сплющимо в один рівень через <parent>.<child>
flat = {}
def _flatten(prefix: str, obj: Any):
if isinstance(obj, dict):
for k, v in obj.items():
key = f"{prefix}.{k}" if prefix else k
_flatten(key, v)
else:
flat[prefix] = obj
_flatten("", data)
return flat
except Exception as exc: # noqa: BLE001
raise UpdateFailed(str(exc)) from exc
