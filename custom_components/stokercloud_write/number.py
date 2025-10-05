from __future__ import annotations
from typing import Optional
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEFAULT_TEMP_MENU, DEFAULT_TEMP_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None
):
    """Старт платформи number (YAML-режим через async_load_platform)."""
    data = hass.data[DOMAIN]
    client = data["client"]
    entity = StokerCloudBoilerSetpointNumber(client)
    async_add_entities([entity], True)


class StokerCloudBoilerSetpointNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Boiler setpoint"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 30
    _attr_native_max_value = 85
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = "box"
    # Стабільний unique_id, щоб сутність не “втрачалась” після оновлень
    _attr_unique_id = "stokercloud_write_boiler_setpoint"

    def __init__(self, client):
        self._client = client
        self._menu = DEFAULT_TEMP_MENU
        self._name_key = DEFAULT_TEMP_NAME
        # Початкове значення-фолбек, щоб інпут був активний відразу:
        self._attr_native_value = 60.0

    async def async_added_to_hass(self) -> None:
        """Спробувати прочитати поточний сетпоінт при додаванні."""
        try:
            data = await self._client.get_output_settings()
            value = self._extract_setpoint(data)
            if value is not None:
                self._attr_native_value = float(value)
                self.async_write_ha_state()
            else:
                _LOGGER.debug("Could not extract setpoint from get_output_settings payload: %s", data)
        except Exception as exc:
            _LOGGER.debug("get_output_settings failed: %s", exc)

    def _extract_setpoint(self, data: dict) -> Optional[float]:
        """ПІДГОТОВКА: підлаштуй під реальну відповідь get_output_settings."""
        try:
            if isinstance(data, dict):
                # варіант 1: вкладена структура
                cur = data
                for k in ("boiler", "temp", "setpoint"):
                    if isinstance(cur, dict) and k in cur:
                        cur = cur[k]
                    else:
                        cur = None
                        break
                if cur is not None:
                    return float(cur)

                # варіант 2: плоскі ключі
                for k in ("boiler.temp", "setpoint"):
                    if k in data and data[k] is not None:
                        return float(data[k])
        except Exception:
            return None
        return None

    async def async_set_native_value(self, value: float) -> None:
        # Записуємо значення через updatevalue.php
        await self._client.update_value(
            menu=self._menu,
            name=self._name_key,
            value=int(round(value)),
        )
        self._attr_native_value = float(value)
        self.async_write_ha_state()
