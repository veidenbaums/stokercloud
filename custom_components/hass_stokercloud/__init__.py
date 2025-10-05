from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DATA_SCHEMA,
    PLATFORMS,
    # конфіг і сервісні ключі
    CONF_TOKEN, CONF_PHPSESSID,
    ATTR_MENU, ATTR_NAME, ATTR_VALUE, ATTR_PHPSESSID,
)
from .api import StokerCloudClient

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """YAML-налаштування інтеграції."""
    conf: dict[str, Any] | None = config.get(DOMAIN)
    if not conf:
        _LOGGER.error("Missing '%s' section in configuration.yaml", DOMAIN)
        return False

    # Валідація за твоєю схемою + нові поля
    conf = DATA_SCHEMA(conf)

    session = async_get_clientsession(hass)

    token = conf[CONF_TOKEN]
    phpsessid = conf.get(CONF_PHPSESSID) or None

    client = StokerCloudClient(session, token, phpsessid)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["client"] = client
    hass.data[DOMAIN]["config"] = conf

    # Реєструємо low-level сервіс для будь-якого запису
    async def _handle_set_value(call: ServiceCall):
        await client.update_value(
            menu=call.data[ATTR_MENU],
            name=call.data[ATTR_NAME],
            value=call.data[ATTR_VALUE],
            phpsessid=call.data.get(ATTR_PHPSESSID) or None,
        )

    hass.services.async_register(DOMAIN, "set_value", _handle_set_value)

    # Піднімаємо твої платформи + нашу нову 'number'
    for platform in PLATFORMS:
        await async_load_platform(hass, platform, DOMAIN, {}, config)

    _LOGGER.info("StokerCloud YAML integration is set up with write support.")
    return True
