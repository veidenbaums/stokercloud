from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature, UnitOfMass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
# RestoreEntity більше не потрібен, бо ми беремо актуальні дані
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN, ATTR_MANUFACTURER, CONF_SERIAL, CONF_NAME,
    DEFAULT_MIN_TEMP, DEFAULT_MAX_TEMP, DEFAULT_STEP,
    BOILER_SCAN_INTERVAL,
)
from .api import StokerCloudWriteApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]

    # --- 1. Координатор для Температури Котла (Setpoint) ---
    async def _upd_boiler_setpoint():
        # Беремо те саме значення, що й sensor.wanted_boiler_temperature
        return await api.async_get_wanted_boiler_temp_from_controller()

    boiler_setpoint_coord = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_boiler_setpoint",
        update_method=_upd_boiler_setpoint,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    # Одразу тягнемо дані при старті, щоб не було "Unknown"
    await boiler_setpoint_coord.async_config_entry_first_refresh()

    # --- 2. Координатор для Бункера (Hopper Content) ---
    async def _upd_hopper_content():
        return await api.async_get_hopper_content_kg()

    hopper_content_coord = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_hopper_content",
        update_method=_upd_hopper_content,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    await hopper_content_coord.async_config_entry_first_refresh()

    # Додаємо обидва намбери
    async_add_entities([
        BoilerSetpointNumber(entry, api, boiler_setpoint_coord),
        HopperContentNumber(entry, api, hopper_content_coord)
    ], update_before_add=True)


class BoilerSetpointNumber(CoordinatorEntity, NumberEntity):
    """
    Керування цільовою температурою котла.
    Тепер використовує CoordinatorEntity, щоб завжди показувати актуальну
    температуру (wanted_boiler_temp) з контролера.
    """
    _attr_has_entity_name = True
    _attr_name = "Boiler temperature setpoint"
    _attr_icon = "mdi:thermometer-chevron-up"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = DEFAULT_MIN_TEMP
    _attr_native_max_value = DEFAULT_MAX_TEMP
    _attr_native_step = DEFAULT_STEP

    def __init__(self, entry: ConfigEntry, api: StokerCloudWriteApi, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        self._entry = entry
        self._api = api
        self._serial = entry.data.get(CONF_SERIAL, "unknown")
        self._attr_unique_id = f"{self._serial}_boiler_temp_setpoint"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=entry.data.get(CONF_NAME) or f"NBE {self._serial}",
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        # Повертає значення з координатора (те саме, що в sensor.wanted_boiler_temperature)
        return self.coordinator.data

    async def async_set_native_value(self, value: float) -> None:
        # 1. Відправляємо команду на котел
        ok = await self._api.async_set_boiler_setpoint(int(round(value)))
        
        if ok:
            # 2. Оптимістичне оновлення: одразу малюємо нове значення в UI, не чекаючи наступного опитування
            self.coordinator.data = float(value)
            self.async_write_ha_state()
            
            # (Опційно) Можна попросити координатор оновитися з API, щоб переконатися
            # await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Failed to set boiler temperature to %s", value)


class HopperContentNumber(CoordinatorEntity, NumberEntity):
    """Залишок пелет у бункері (кг) з можливістю редагування + періодичним опитуванням."""

    _attr_has_entity_name = True
    _attr_name = "Hopper content"
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0.0
    _attr_native_max_value = 5000.0
    _attr_native_step = 1.0
    _attr_icon = "mdi:silo"

    def __init__(self, entry: ConfigEntry, api: StokerCloudWriteApi, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        self._entry = entry
        self._api = api
        self._serial = entry.data.get(CONF_SERIAL, "unknown")
        self._attr_unique_id = f"{self._serial}_hopper_content"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=(entry.data.get(CONF_NAME) or f"NBE {self._serial}"),
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data

    async def async_set_native_value(self, value: float) -> None:
        # 1) Миттєво показуємо нове значення в UI (оптимістично)
        self.coordinator.data = float(value)
        self.async_write_ha_state()

        # 2) Шлемо POST form-data на бекенд
        await self._api.async_set_hopper_content_kg(float(value))
