from __future__ import annotations
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult


from .const import DOMAIN, CONF_SERIAL, CONF_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL


# ⚠️ Спрощена версія без перевірки API, щоб виключити імпортні помилки під час запуску флоу
# Після того як флоу завантажиться, повернемо валідацію.


class StokerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
VERSION = 1


async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
errors: dict[str, str] = {}
if user_input is not None:
serial = user_input[CONF_SERIAL].strip()
token = user_input[CONF_TOKEN].strip()
scan = user_input.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds()))


await self.async_set_unique_id(serial)
self._abort_if_unique_id_configured()
return self.async_create_entry(
title=f"StokerCloud {serial}",
data={
CONF_SERIAL: serial,
CONF_TOKEN: token,
CONF_SCAN_INTERVAL: scan,
},
)


schema = vol.Schema(
{
vol.Required(CONF_SERIAL): str,
vol.Required(CONF_TOKEN): str,
vol.Optional(CONF_SCAN_INTERVAL, default=int(DEFAULT_SCAN_INTERVAL.total_seconds())): int,
}
)
return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
