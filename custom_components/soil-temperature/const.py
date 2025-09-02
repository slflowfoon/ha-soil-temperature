"""Constants for the Soil Temperature integration."""

DOMAIN = "soil_temperature"

# Configuration
CONF_UNIT_SYSTEM = "unit_system"
UNIT_SYSTEM_IMPERIAL = "imperial"
UNIT_SYSTEM_METRIC = "metric"
DEFAULT_UNIT_SYSTEM = UNIT_SYSTEM_IMPERIAL

# Configuration Defaults
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
DEFAULT_SCAN_INTERVAL = 60  # minutes

# API
API_ENDPOINT = "https://soiltemperature.app/api/weatherTimeline?lat={lat}&lng={lng}"
GEOCODE_API_ENDPOINT = "https://soiltemperature.app/api/geocodeReverse?lat={lat}&lng={lng}"

# Sensor Information
SENSOR_TEMPERATURE_NAME = "Soil Temperature"
SENSOR_MOISTURE_NAME = "Soil Moisture"
SENSOR_UNIT_TEMPERATURE_IMPERIAL = "°F"
SENSOR_UNIT_TEMPERATURE_METRIC = "°C"
SENSOR_UNIT_MOISTURE = "m³/m³"

# Data Keys from API
SOIL_TEMPERATURE_KEYS = [
    "soil_temperature_0cm",
    "soil_temperature_6cm",
    "soil_temperature_10cm",
    "soil_temperature_18cm",
    "soil_temperature_54cm",
]

SOIL_MOISTURE_KEYS = [
    "soil_moisture_0_1cm",
    "soil_moisture_1_3cm",
    "soil_moisture_3_9cm",
    "soil_moisture_10cm",
    "soil_moisture_9_27cm",
    "soil_moisture_27_81cm",
]

# Summary types
SUMMARY_TYPES = ["max", "min", "mean"]
