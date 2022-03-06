import aiohttp

from collections import OrderedDict

import voluptuous as vol
from homeassistant import config_entries


from .const import DOMAIN, LOGIN_RESULT_OK, LOGIN_RESULT_UNAUTHORIZED
from .qustodioapi import QustodioApi


@config_entries.HANDLERS.register(DOMAIN)
class BlueprintFlowHandler(config_entries.ConfigFlow):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(
        self, user_input={}
    ):  # pylint: disable=dangerous-default-value
        """Handle a flow initialized by the user."""
        self._errors = {}
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        if self.hass.data.get(DOMAIN):
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            result = await self._show_config_form(user_input)

            api = QustodioApi(user_input["username"], user_input["password"])
            valid = await api.login()

            if valid == LOGIN_RESULT_OK:
                # add profiles
                user_input["profiles"] = await api.get_data()
                result = self.async_create_entry(title="", data=user_input)

            if valid == LOGIN_RESULT_UNAUTHORIZED:
                self._errors["base"] = "auth"

            return result

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        # Defaults
        username = ""
        password = ""

        if user_input is not None:
            if "username" in user_input:
                username = user_input["username"]
            if "password" in user_input:
                password = user_input["password"]

        data_schema = OrderedDict()
        data_schema[vol.Required("username", default=username)] = str
        data_schema[vol.Required("password", default=password)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):  # pylint: disable=unused-argument
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})
