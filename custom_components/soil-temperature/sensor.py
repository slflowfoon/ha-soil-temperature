"""Sensor platform for the Soil Temperature integration."""
from __future__ import annotations
from typing import Callable

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_UNIT_SYSTEM,
    UNIT_SYSTEM_METRIC,
    SENSOR_TEMPERATURE_NAME,
    SENSOR_MOISTURE_NAME,
    SENSOR_UNIT_TEMPERATURE_IMPERIAL,
    SENSOR_UNIT_TEMPERATURE_METRIC,
    SENSOR_UNIT_MOISTURE,
    SOIL_TEMPERATURE_KEYS,
    SOIL_MOISTURE_KEYS,
    SUMMARY_TYPES,
)
from .coordinator import SoilTemperatureDataUpdateCoordinator


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: SoilTemperatureDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities: list[SensorEntity] = []
    unit_system = config_entry.data.get(CONF_UNIT_SYSTEM)

    # Create Current Sensors
    for key in SOIL_TEMPERATURE_KEYS:
        entities.append(SoilTemperatureCurrentSensor(coordinator, key, SENSOR_TEMPERATURE_NAME, unit_system))
    for key in SOIL_MOISTURE_KEYS:
        entities.append(SoilTemperatureCurrentSensor(coordinator, key, SENSOR_MOISTURE_NAME, unit_system))

    # Create Summary Sensors
    for summary_type in SUMMARY_TYPES:
        for key in SOIL_TEMPERATURE_KEYS:
            entities.append(SoilTemperatureSummarySensor(coordinator, key, summary_type, SENSOR_TEMPERATURE_NAME, unit_system))
        for key in SOIL_MOISTURE_KEYS:
            entities.append(SoilTemperatureSummarySensor(coordinator, key, summary_type, SENSOR_MOISTURE_NAME, unit_system))
            
    async_add_entities(entities)


class SoilTemperatureBaseSensor(CoordinatorEntity[SoilTemperatureDataUpdateCoordinator], SensorEntity):
    """Base class for a Soil Temperature sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: SoilTemperatureDataUpdateCoordinator,
        data_key: str,
        sensor_type: str,
        unit_system: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._unit_system = unit_system
        self._is_temp = sensor_type == SENSOR_TEMPERATURE_NAME

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name="Soil Conditions",
            manufacturer="SoilTemperature.app",
            entry_type="service",
        )
        
        # Set device class and units
        if self._is_temp:
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = (
                SENSOR_UNIT_TEMPERATURE_METRIC
                if self._unit_system == UNIT_SYSTEM_METRIC
                else SENSOR_UNIT_TEMPERATURE_IMPERIAL
            )
        else:
            self._attr_device_class = SensorDeviceClass.MOISTURE
            self._attr_native_unit_of_measurement = SENSOR_UNIT_MOISTURE

    def _process_value(self, value: float | None) -> float | None:
        """Process the raw value for the sensor."""
        if value is None:
            return None
        
        if self._is_temp:
            if self._unit_system == UNIT_SYSTEM_METRIC:
                return round(fahrenheit_to_celsius(value), 2)
            return round(value, 2)
        else:
            # Convert moisture fraction to percentage
            return round(value * 100, 2)


class SoilTemperatureCurrentSensor(SoilTemperatureBaseSensor):
    """Representation of a current soil condition sensor."""

    def __init__(
        self,
        coordinator: SoilTemperatureDataUpdateCoordinator,
        data_key: str,
        sensor_type: str,
        unit_system: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, data_key, sensor_type, unit_system)
        
        self._attr_unique_id = f"{coordinator.entry.entry_id}_current_{data_key}"
        self._attr_name = f"Current {sensor_type} {data_key.split('_')[-1]}"
        
    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "current" in self.coordinator.data:
            raw_value = self.coordinator.data["current"].get(self._data_key)
            return self._process_value(raw_value)
        return None


class SoilTemperatureSummarySensor(SoilTemperatureBaseSensor):
    """Representation of a daily summary soil condition sensor."""

    _attr_entity_registry_enabled_default = False  # Summaries are disabled by default

    def __init__(
        self,
        coordinator: SoilTemperatureDataUpdateCoordinator,
        data_key: str,
        summary_type: str,
        sensor_type: str,
        unit_system: str,
    ) -> None:
        """Initialize the summary sensor."""
        super().__init__(coordinator, data_key, sensor_type, unit_system)
        self._summary_type = summary_type

        self._attr_unique_id = f"{coordinator.entry.entry_id}_summary_{summary_type}_{data_key}"
        self._attr_name = f"Today's {summary_type.capitalize()} {sensor_type} {data_key.split('_')[-1]}"
        
    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if (
            self.coordinator.data
            and "summary" in self.coordinator.data
            and self._data_key in self.coordinator.data["summary"]
        ):
            raw_value = self.coordinator.data["summary"][self._data_key].get(self._summary_type)
            return self._process_value(raw_value)
        return None
