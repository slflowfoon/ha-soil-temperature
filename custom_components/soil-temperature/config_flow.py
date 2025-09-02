"""Config flow for Soil Temperature integration."""
import voluptuous as vol

from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_SCAN_INTERVAL

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_UNIT_SYSTEM,
    UNIT_SYSTEM_IMPERIAL,
    UNIT_SYSTEM_METRIC,
    DEFAULT_UNIT_SYSTEM,
)


class SoilTemperatureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Soil Temperature."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SoilTemperatureOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_LATITUDE]}-{user_input[CONF_LONGITUDE]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Soil Temperature ({user_input[CONF_LATITUDE]}, {user_input[CONF_LONGITUDE]})",
                data=user_input
            )

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
    """Handle an options flow for Soil Temperature."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
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
