"""DataUpdateCoordinator for the Soil Temperature integration."""
import logging
from datetime import timedelta, date
import statistics

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_SCAN_INTERVAL

from .const import (
    API_ENDPOINT,
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    SOIL_TEMPERATURE_KEYS,
    SOIL_MOISTURE_KEYS,
)

_LOGGER = logging.getLogger(__name__)


class SoilTemperatureDataUpdateCoordinator(DataUpdateCoordinator):
    """A coordinator to fetch data from the Soil Temperature API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        scan_interval = self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    def _process_timeline_data(self, timeline: list[dict]) -> dict:
        """Process timeline data to get today's summary."""
        today = date.today()
        today_data = {key: [] for key in SOIL_TEMPERATURE_KEYS + SOIL_MOISTURE_KEYS}
        
        for entry in timeline:
            entry_date = date.fromtimestamp(entry.get("time", 0))
            if entry_date == today:
                for key in today_data:
                    if key in entry and entry[key] is not None:
                        today_data[key].append(entry[key])
        
        summary = {}
        for key, values in today_data.items():
            if not values:
                summary[key] = {"max": None, "min": None, "mean": None}
                continue

            summary[key] = {
                "max": max(values),
                "min": min(values),
                "mean": round(statistics.mean(values), 2),
            }
        return summary

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        session = async_get_clientsession(self.hass)
        lat = self.entry.data[CONF_LATITUDE]
        lng = self.entry.data[CONF_LONGITUDE]
        url = API_ENDPOINT.format(lat=lat, lng=lng)

        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                if "timeline" not in data or "mostRecentReading" not in data:
                    raise UpdateFailed("Invalid data structure received from API")

                summary_data = self._process_timeline_data(data["timeline"])
                
                return {
                    "current": data["mostRecentReading"],
                    "summary": summary_data,
                }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Soil Temperature API: {err}")
