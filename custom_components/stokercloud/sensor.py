from __future__ import annotations
import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, UnitOfPower, UnitOfMass, PERCENTAGE
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ATTR_MANUFACTURER, CONF_SERIAL, CONF_NAME, BOILER_SCAN_INTERVAL
from .api import StokerCloudWriteApi

# fallback for illuminance units (if needed)
try:
    from homeassistant.const import UnitOfIlluminance
    ILLUM_UNIT = UnitOfIlluminance.LUX
except Exception:
    ILLUM_UNIT = "lx"

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

    # NEW: raw state code (miscdata.state.value), e.g. 'state_5'
    async def _upd_state_code():
        return await api.async_get_state_code_from_controller()

    # (optional) photo sensor lux, if you use it
    async def _upd_photo_lux():
        try:
            if hasattr(api, "async_get_photo_sensor_lux_from_controller"):
                return await api.async_get_photo_sensor_lux_from_controller()
        except Exception as e:
            _LOGGER.debug("Photo sensor update failed: %s", e)
        return None
    
    async def _upd_pump_state():
        return await api.async_get_pump_state_from_controller()
    
    async def _upd_oxygen():
        return await api.async_get_oxygen_from_controller()
    
    async def _upd_hopper_cons_24h():
        return await api.async_get_hopper_consumption_24h_kg()

    # --- NEW: Update hopper remaining amount (kg) for the sensor ---
    async def _upd_hopper_content():
        return await api.async_get_hopper_content_kg()

    async def _upd_dhw_difference_under():
        return await api.async_get_dhw_difference_under_from_controller()

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

    # NEW: coordinator for the state code
    state_code_coord = DataUpdateCoordinator[str | None](
        hass, _LOGGER, name=f"{DOMAIN}_state_code",
        update_method=_upd_state_code,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )

    # (optional) lux from photo sensor
    photo_lux_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_photo_lux",
        update_method=_upd_photo_lux,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    pump_state_coord = DataUpdateCoordinator[str | None](
        hass, _LOGGER, name=f"{DOMAIN}_pump_state",
        update_method=_upd_pump_state,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    oxygen_coord = DataUpdateCoordinator[float | None](
        hass, _LOGGER, name=f"{DOMAIN}_oxygen",
        update_method=_upd_oxygen,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    hopper_cons_24h_coord = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_hopper_cons_24h",
        update_method=_upd_hopper_cons_24h,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )
    
    # --- NEW: Hopper content coordinator ---
    hopper_content_coord = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_hopper_content_sensor",
        update_method=_upd_hopper_content,
        update_interval=timedelta(seconds=BOILER_SCAN_INTERVAL),
    )

    dhw_difference_under_coord = DataUpdateCoordinator[float | None](
        hass,
        _LOGGER,
        name=f"{DOMAIN}_dhw_difference_under_sensor",
        update_method=_upd_dhw_difference_under,
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

    await state_code_coord.async_config_entry_first_refresh()
    await photo_lux_coord.async_config_entry_first_refresh()
    await pump_state_coord.async_config_entry_first_refresh()
    await oxygen_coord.async_config_entry_first_refresh()
    await hopper_cons_24h_coord.async_config_entry_first_refresh()
    
    # --- NEW: Initial update ---
    await hopper_content_coord.async_config_entry_first_refresh()

    await dhw_difference_under_coord.async_config_entry_first_refresh()

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
            PumpStateSensor(entry, pump_state_coord),
            OxygenSensor(entry, oxygen_coord),
            HopperConsumption24hSensor(entry, hopper_cons_24h_coord),
            StateTextSensor(entry, state_code_coord),
            PhotoIlluminanceSensor(entry, photo_lux_coord),
            
            # --- NEW: Add sensor ---
            HopperContentSensor(entry, hopper_content_coord),

            DhwDifferenceUnder(entry, dhw_difference_under_coord),
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


class StateTextSensor(CoordinatorEntity[DataUpdateCoordinator[str | None]], SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:flash"

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[str | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_state"
        self._attr_name = "State"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def native_value(self) -> str | None:
        code = self.coordinator.data
        if not code:
            return None
        mapping = {
            "state_14": "OFF",
            "state_5": "Power",
            "state_2": "Ignition",
        }
        return mapping.get(str(code), str(code))

    @property
    def extra_state_attributes(self):
        return {"raw_code": self.coordinator.data}


class PhotoIlluminanceSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_device_class = SensorDeviceClass.ILLUMINANCE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:brightness-5"
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = ILLUM_UNIT

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_photo_lux"
        self._attr_name = "Photo sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data


class PumpStateSensor(CoordinatorEntity[DataUpdateCoordinator[str | None]], SensorEntity):
    _attr_icon = "mdi:pump"
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[str | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_pump_state"
        self._attr_name = "Pump State"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> str | None:
        val = self.coordinator.data
        if val is None:
            return None
        return val

    @property
    def extra_state_attributes(self):
        return {"source_path": "leftoutput.output-2.val"}


class OxygenSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Oxygen"
    _attr_icon = "mdi:gas-cylinder"
    _attr_device_class = SensorDeviceClass.POWER_FACTOR
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_oxygen"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data

    @property
    def extra_state_attributes(self):
        return {"source_path": "boilerdata[id=12].value"}


class HopperConsumption24hSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Pellet consumption (last 24h)"
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        self._attr_unique_id = f"{serial}_hopper_consumption_24h"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data

    @property
    def extra_state_attributes(self):
        return {
            "source_array": "hopperdata",
            "source_id": "3",
            "source_selection": "hopper2",
            "meaning": "Consumption last 24 h.",
            "api_endpoint": "controllerdata2.php",
        }


# --- NEW: Hopper pellet remainder sensor class ---
class HopperContentSensor(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Hopper content"
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.WEIGHT  # You can add the device class "Weight".
    _attr_icon = "mdi:silo"

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        # We add _sensor to avoid an ID conflict with number.hopper_content.
        self._attr_unique_id = f"{serial}_hopper_content_sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data

class DhwDifferenceUnder(CoordinatorEntity[DataUpdateCoordinator[float | None]], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "DHW difference under"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_icon = "mdi:thermometer"

    def __init__(self, entry: ConfigEntry, coordinator: DataUpdateCoordinator[float | None]):
        super().__init__(coordinator)
        serial = entry.data.get(CONF_SERIAL, "unknown")
        dev_name = entry.data.get(CONF_NAME) or f"NBE {serial}"
        # We add _sensor to avoid an ID conflict with number.hopper_content.
        self._attr_unique_id = f"{serial}_dhw_difference_under_sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=ATTR_MANUFACTURER,
            name=dev_name,
            model="StokerCloud",
        )

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data
