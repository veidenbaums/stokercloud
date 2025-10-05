from __future__ import annotations
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult


from .const import DOMAIN, CONF_SERIAL, CONF_TOKEN, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .api import StokerApi


class StokerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
VERSION = 1


async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
errors = {}
if user_input is not None:
serial = user_input[CONF_SERIAL].strip()
token = user_input[CONF_TOKEN].strip()
scan = user_input.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds()))


api = StokerApi(serial=serial, token=token)
ok, err = await api.async_validate()
if ok:
await self.async_set_unique_id(serial)
self._abort_if_unique_id_configured()
return self.async_create_entry(title=f"StokerCloud {serial}", data={
CONF_SERIAL: serial,
CONF_TOKEN: token,
CONF_SCAN_INTERVAL: scan,
})
errors["base"] = "cannot_connect"


schema = vol.Schema({
vol.Required(CONF_SERIAL): str,
vol.Required(CONF_TOKEN): str,
vol.Optional(CONF_SCAN_INTERVAL, default=int(DEFAULT_SCAN_INTERVAL.total_seconds())): int,
})
return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


@callback
def async_get_options_flow(self, config_entry):
return StokerOptionsFlow(config_entry)


class StokerOptionsFlow(config_entries.OptionsFlow):
def __init__(self, entry: config_entries.ConfigEntry) -> None:
self.entry = entry


async def async_step_init(self, user_input=None):
if user_input is not None:
return self.async_create_entry(title="", data=user_input)


schema = vol.Schema({
vol.Optional(CONF_SCAN_INTERVAL, default=self.entry.data.get(CONF_SCAN_INTERVAL, int(DEFAULT_SCAN_INTERVAL.total_seconds()))): int,
})
return self.async_show_form(step_id="init", data_schema=schema)
