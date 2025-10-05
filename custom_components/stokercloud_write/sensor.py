from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfPower, PERCENTAGE
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_SERIAL, CONF_NAME, BOILER_SCAN_INTERVAL
from .api import StokerCloudWriteApi

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    api: StokerCloudWriteApi = hass.data[DOMAIN][entry.entry_id]

    async def _upd_boiler():
        return await api.async_get_boiler_temperature_from_controller()

    async def _upd_external():
        return await api.async_get_external_temperature_from_controller()

    async def _upd_wanted_boiler():
        return await api.async_get_wanted_boiler_temp_from_controller()

    async def _upd_dhw():
        return await api.async_get_dhw_temperature_from_controller()

    async def _upd_dhw_wanted():
        return await api.async_get_dhw_wanted_temperature_from_controller()

    async def _upd_shaft():
        return await api.async_get_shaft_temperature_from_controller()

    async def _upd_output_kw():
        return await api.async_get_output_kw_from_controller()

    async def _upd_output_pct():
        return await api.async_get_output_pct_from_controller()

    boiler_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_boiler_temp",
        update_method=_upd_boiler,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    external_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_external_temp",
        update_method=_upd_external,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    wanted_boiler_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_wanted_boiler_temp",
        update_method=_upd_wanted_boiler,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    dhw_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_dhw_temp",
        update_method=_upd_dhw,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    dhw_wanted_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_dhw_wanted_temp",
        update_method=_upd_dhw_wanted,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    shaft_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_shaft_temp",
        update_method=_upd_shaft,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    output_kw_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_output_kw",
        update_method=_upd_output_kw,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    output_pct_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_output_pct",
        update_method=_upd_output_pct,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )

    await boiler_coord.async_config_entry_first_refresh()
    await external_coord.async_config_entry_first_refresh()
    await wanted_boiler_coord.async_config_entry_first_refresh()
    await dhw_coord.async_config_entry_first_refresh()
    await dhw_wanted_coord.async_config_entry_first_refresh()
    await shaft_coord.async_config_entry_first_refresh()
    await output_kw_coord.async_config_entry_first_refresh()
    await output_pct_coord.async_config_entry_first_refresh()

    async_add_entities(
        [
            BoilerTemperatureSensor(entry, boiler_coord),
            ExternalTemperatureSensor(entry, external_coord),
            WantedBoilerTemperatureSensor(entry, wanted_boiler_coord),
            DhwTemperatureSensor(entry, dhw_coord),
            DhwWantedTemperatureSensor(entry, dhw_wanted_coord),
            ShaftTemperatureSensor(entry, shaft_coord),
            OutputPowerKwSensor(entry, output_kw_coord),
            OutputPowerPercentSensor(entry, output_pct_coord),
        ],
        True,
    )


class _BaseTempSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None], unique_suffix: str, name: str):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_{unique_suffix}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data


class BoilerTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "boiler_temperature", "Boiler temperature")


class ExternalTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "external_temperature", "External temperature")


class WantedBoilerTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "wanted_boiler_temperature", "Wanted boiler temperature")


class DhwTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "dhw_temperature", "Hot water temperature")


class DhwWantedTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "dhw_wanted_temperature", "Hot water wanted temperature")


class ShaftTemperatureSensor(_BaseTempSensor):
    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(entry, coordinator, "shaft_temperature", "Shaft temperature")


class OutputPowerKwSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_icon = "mdi:flash"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_power_kw"
        self._attr_name = "Power (kW)"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data


class OutputPowerPercentSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:percent"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_power_percent"
        self._attr_name = "Power (%)"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data
