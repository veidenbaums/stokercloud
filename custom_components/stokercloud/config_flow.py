from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SERIAL, CONF_TOKEN, CONF_NAME


class StokerCloudWriteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """StokerCloud Write setup wizard."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            serial = user_input[CONF_SERIAL]
            # Avoid duplicates by serial number.
            await self.async_set_unique_id(serial)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or f"NBE {serial}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL): str,
                vol.Required(CONF_TOKEN): str,
                vol.Optional(CONF_NAME, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
