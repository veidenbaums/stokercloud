from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SERIAL_NUMBER, CONF_TOKEN, CONF_PHPSESSID

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_SERIAL_NUMBER): str,
    vol.Required(CONF_TOKEN): str,
    vol.Optional(CONF_PHPSESSID, default=""): str,
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for StokerCloud Write."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        serial = user_input[CONF_SERIAL_NUMBER].strip()

        # не дозволяємо дублікати за серійником
        await self.async_set_unique_id(serial)
        self._abort_if_unique_id_configured()

        data = {
            CONF_SERIAL_NUMBER: serial,
            CONF_TOKEN: user_input[CONF_TOKEN].strip(),
        }
        phpsessid = user_input.get(CONF_PHPSESSID, "").strip()
        if phpsessid:
            data[CONF_PHPSESSID] = phpsessid

        return self.async_create_entry(title=f"StokerCloud ({serial})", data=data)

    async def async_step_import(self, import_config):
        """Якщо колись додавали через YAML — можна імпортувати (опційно)."""
        return await self.async_step_user(import_config)
