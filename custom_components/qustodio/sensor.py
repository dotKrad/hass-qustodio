import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN_DATA,
    ICON_IN_TIME,
    ICON_NO_TIME,
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    # _LOGGER.error(f"Adding fpl accounts: {str(discovery_info)}")
    # async_add_entities([QustodioSensor(hass, discovery_info)], True)
    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    profiles = config_entry.data.get("profiles")

    for profile_id in profiles:
        async_add_devices([QustodioSensor(hass, profiles[profile_id])], True)


class QustodioSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = config.get("name", DEFAULT_NAME)
        self._id = config.get("id")
        self.entity_id = f"sensor.{DOMAIN}_{self._name}"

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        if "data" in self.hass.data[DOMAIN_DATA]:
            data = self.hass.data[DOMAIN_DATA]["data"][self._id]

            self._state = data["time"]

            # Set/update attributes
            self.attr["attribution"] = ATTRIBUTION
            self.attr["time"] = data["time"]
            self.attr["current_device"] = data["current_device"]
            self.attr["is_online"] = data["is_online"]
            self.attr["quota"] = data["quota"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return "{}{}".format(DOMAIN, self._id)

    # @property
    # def device_info(self):
    #    return {
    #        "identifiers": {(DOMAIN, "account1234")},
    #        "name": DEFAULT_NAME,
    #        "manufacturer": DOMAIN,
    #    }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        if (
            "time" in self.attr
            and "quota" in self.attr
            and self.attr["time"] < self.attr["quota"]
        ):
            return ICON_IN_TIME
        return ICON_NO_TIME

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
