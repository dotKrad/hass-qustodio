"""
TODO
DETAILS
"""
import logging

from homeassistant.components.device_tracker import (
    DOMAIN as PLATFORM_DOMAIN,
    SOURCE_TYPE_GPS,
)
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_NAME, DOMAIN_DATA, ATTRIBUTION


_LOGGER = logging.getLogger(__name__)

# pylint: disable=unused-argument
async def async_setup_entry(
    hass: HomeAssistantType, config_entry: ConfigEntry, async_add_entities
):
    """Set up the tracker."""

    profiles = config_entry.data.get("profiles")

    trackers = []

    for profile_id in profiles:
        trackers.append(QustodioTrackerEntity(hass, profiles[profile_id]))

    async_add_entities(trackers, True)

    tracker_ids = hass.states.async_entity_ids(PLATFORM_DOMAIN)
    """
    for _, device in api.devices.items():

        # Dirty hack for legacy device tracker came from known_devices.yaml
        entity_id = "{}.{}".format(PLATFORM_DOMAIN, slugify(device.pandora_id))
        if entity_id in tracker_ids:
            _LOGGER.warning(
                "Entity %s is obsolete. You have to remove it from known_devices.yaml",
                entity_id,
            )
            hass.states.async_remove(entity_id)

        trackers.append(QustodioTrackerEntity(hass, device))

    async_add_entities(trackers, False)
    """


class QustodioTrackerEntity(TrackerEntity):
    def __init__(self, hass: HomeAssistantType, config):

        self._hass = hass
        # self._device = device
        self._latitude = None
        self._longitude = None
        self._accuracy = 0
        self.attr = {}
        self._name = config.get("name", DEFAULT_NAME)
        self._id = config.get("id")

        self.entity_id = f"{PLATFORM_DOMAIN}.{DOMAIN}_{self._name}"

    async def async_update(self):
        """Update the platform."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data()

        # Get new data (if any)
        if "data" in self.hass.data[DOMAIN_DATA]:
            if self._id in self.hass.data[DOMAIN_DATA]["data"]:
                data = self.hass.data[DOMAIN_DATA]["data"][self._id]

                self._state = data["time"]

                # Set/update attributes
                self.attr["attribution"] = ATTRIBUTION
                self._latitude = data["latitude"]
                self._longitude = data["longitude"]
                self._accuracy = data["accuracy"]
                self.attr["last_seen"] = data["lastseen"]

    @property
    def unique_id(self) -> str:
        """Return the entity_id of the binary sensor."""
        return "{}{}{}".format(PLATFORM_DOMAIN, DOMAIN, self._id)

    @property
    def name(self) -> str:
        """Return device name for this tracker entity."""
        return f"{self._name}"

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self._latitude

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self._longitude

    @property
    def location_accuracy(self):
        return self._accuracy

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def should_poll(self):
        """No polling for entities that have location pushed."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

    """
    @callback
    def _update_callback(self, force=False):
        """ """
        if self._latitude != self._device.x or self._longitude != self._device.y:
            self._latitude = self._device.x
            self._longitude = self._device.y
            self.async_write_ha_state()

    async def async_added_to_hass(self):
        "When entity is added to hass.""
        self.async_on_remove(
            self._hass.data[DOMAIN].async_add_listener(self._update_callback)
        )
        self._update_callback(True)
    """