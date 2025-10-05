from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

# Поля конфігурації через UI:
# - serial (обов'язково)
# - token (опційно, але потрібен для write-операцій)
USER_SCHEMA = vol.Schema(
    {
        vol.Required("serial"): str,
        vol.Optional("token"): str,
    }
)

# Опції інтеграції (через "Configure"):
OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=10, max=3600)
        ),
    }
)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Підставимо поточні значення у форму
        cur = {
            "scan_interval": self.config_entry.options.get(
                "scan_interval", DEFAULT_SCAN_INTERVAL
            ),
        }
        return self.async_show_form(step_id="init", data_schema=_options_schema(cur))


def _options_schema(cur: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required("scan_interval", default=cur["scan_interval"]): vol.All(
                int, vol.Range(min=10, max=3600)
            ),
        }
    )


class StokercloudWriteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для інтеграції StokerCloud Write+Read."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Початковий крок — форма підключення."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=USER_SCHEMA)

        serial = user_input["serial"].strip()
        token = user_input.get("token")

        # (Опційно) тут можна зробити валідацію через API (ping status),
        # але щоб не падати без інтернету — поки просто приймаємо.

        # Уникнути дублю записів на один і той самий serial
        await self.async_set_unique_id(f"{DOMAIN}_{serial}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"StokerCloud {serial}",
            data={"serial": serial, "token": token},
        )

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Опційний flow для налаштувань (scan_interval)."""
        return OptionsFlowHandler(config_entry)
