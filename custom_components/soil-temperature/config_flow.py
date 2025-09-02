import logging
import voluptuous as vol
import aiohttp

from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_UNIT_SYSTEM,
    UNIT_SYSTEM_IMPERIAL,
    UNIT_SYSTEM_METRIC,
    DEFAULT_UNIT_SYSTEM,
    GEOCODE_API_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class SoilTemperatureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SoilTemperatureOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_LATITUDE]}-{user_input[CONF_LONGITUDE]}")
            self._abort_if_unique_id_configured()

            lat = user_input[CONF_LATITUDE]
            lng = user_input[CONF_LONGITUDE]
            
            title = f"Soil Temperature ({city})"

            try:
                session = async_get_clientsession(self.hass)
                url = GEOCODE_API_ENDPOINT.format(lat=lat, lng=lng)
                async with session.get(url) as response:
                    response.raise_for_status()
                    geo_data = await response.json(content_type=None)
                    
                    if city := geo_data.get("city"):
                        title = f"Soil Temperature ({city})"
                    else:
                        _LOGGER.warning("Geocode response did not contain a city: %s", geo_data)

            except aiohttp.ClientError as err:
                _LOGGER.warning("Failed to connect to geocode API, using coordinates as title: %s", err)
            except Exception as err:
                _LOGGER.error("An unexpected error occurred during geocoding: %s", err)

            return self.async_create_entry(title=title, data=user_input)

        default_latitude = self.hass.config.latitude
        default_longitude = self.hass.config.longitude

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_LATITUDE, default=default_latitude): vol.Coerce(float),
                    vol.Required(CONF_LONGITUDE, default=default_longitude): vol.Coerce(float),
                    vol.Required(CONF_UNIT_SYSTEM, default=DEFAULT_UNIT_SYSTEM): vol.In(
                        [UNIT_SYSTEM_IMPERIAL, UNIT_SYSTEM_METRIC]
                    ),
                }
            ),
            errors=errors,
        )


class SoilTemperatureOptionsFlowHandler(config_entries.OptionsFlow):

    def __init__(self, config_entry: config_entries.ConfigEntry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
        )
