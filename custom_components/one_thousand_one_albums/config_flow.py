"""Config flow for 1001 Albums."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_PROJECT, DEFAULT_PROJECT, DOMAIN, build_project_url


class OneThousandOneAlbumsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 1001 Albums."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            project = user_input[CONF_PROJECT].strip().strip("/")
            if not project:
                project = DEFAULT_PROJECT
            user_input[CONF_PROJECT] = project
            return self.async_create_entry(title=project, data=user_input)

        schema = vol.Schema({vol.Required(CONF_PROJECT, default=DEFAULT_PROJECT): str})
        return self.async_show_form(step_id="user", data_schema=schema)
