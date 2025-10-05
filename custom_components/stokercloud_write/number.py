from __future__ import annotations
from typing import Optional

from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DEFAULT_TEMP_MENU, DEFAULT_TEMP_NAME

async def async_setup_platform(
    hass: HomeAssistant,
    config,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None
):
    """Старт платформи number (YAML-режим через async_load_platform)."""
    data = hass.data[DOMAIN]
    client = data["client"]

    async_add_entities([StokerCloudBoilerSetpointNumber(client)], True)

class StokerCloudBoilerSetpointNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Boiler setpoint"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 30
    _attr_native_max_value = 85
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "°C"
    _attr_mode = "box"  # дозволяє ручний ввід

    def __init__(self, client):
        self._client = client
        self._menu = DEFAULT_TEMP_MENU
        self._name_key = DEFAULT_TEMP_NAME
        self._state: Optional[float] = None
        # unique_id не обов’язковий у YAML-платформі, але можна задати стабільний
        self._attr_unique_id = "stokercloud_boiler_setpoint"

    @property
    def native_value(self) -> Optional[float]:
        return self._state

    async def async_added_to_hass(self) -> None:
        """Спробувати прочитати поточний сетпоінт при додаванні."""
        try:
            data = await self._client.get_output_settings()
            value = self._extract_setpoint(data)
            if value is not None:
                self._state = float(value)
                self.async_write_ha_state()
        except Exception:
            # не фейлимося — все одно дозволимо встановлювати значення
            pass

    def _extract_setpoint(self, data: dict) -> Optional[float]:
        """
        ПІДГОТОВКА: якщо знаєш точну структуру JSON з get_output_settings.php — підкоригуй.
        Типові варіанти:
          - data["boiler"]["temp"]["setpoint"]
          - data["boiler.temp"]
          - data["setpoint"]
        """
        try:
            if isinstance(data, dict):
                # спроба по вкладених ключах
                cur = data
                for k in ("boiler", "temp", "setpoint"):
                    if isinstance(cur, dict) and k in cur:
                        cur = cur[k]
                    else:
                        cur = None
                        break
                if cur is not None:
                    return float(cur)

                # плоскі ключі
                for k in ("boiler.temp", "setpoint"):
                    if k in data and data[k] is not None:
                        return float(data[k])
        except Exception:
            return None
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self._client.update_value(
            menu=self._menu,
            name=self._name_key,
            value=int(round(value)),
        )
        self._state = float(value)
        self.async_write_ha_state()
