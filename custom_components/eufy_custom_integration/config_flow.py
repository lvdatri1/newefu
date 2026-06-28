"""
Config flow for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 The config flow handles the UI-based setup wizard that users follow when
 adding "Eufy Custom Integration" via Settings -> Devices & Services.
 It collects connection details (host, port, username, password) and creates
 a ConfigEntry that persists these settings.

================================================================================
 STEPS
================================================================================

 1. user:        The initial form. Collects host, port, credentials,
                 and poll interval. On submit, creates the config entry.

 FUTURE STEPS (to implement):
   - async_step_reauth:    Handle credential expiry.
   - async_step_reconfigure: Allow editing options after setup.

================================================================================
 EXTENSION POINTS
================================================================================

 To add more config options:
   1. Add new fields to the schema in async_step_user().
   2. Add corresponding CONF_* constants in const.py.
   3. Read them in coordinator.py or platform files.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_PORT,
    DOMAIN,
)


class EufyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eufy Custom Integration.

    This is the UI workflow that runs when a user clicks "Add Integration"
    in Home Assistant. It presents a form, validates input, and creates
    a ConfigEntry that persists the connection settings.

    Usage:
        This class is auto-discovered by HA via the ConfigFlow domain.
        No manual instantiation is needed.
    """

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial configuration step.

        If user_input is None, show the configuration form.
        If user_input is provided, create the config entry.

        The form collects:
          - host (required):          IP address or hostname of Eufy hub
          - username (required):      Eufy account username
          - password (required):      Eufy account password
          - port (optional, default 5222):  Connection port
          - poll_interval (optional, default 30s):  How often to poll

        Args:
            user_input: Dict of user-provided values, or None to show form.

        Returns:
            A FlowResult (either the form to display, or a created entry).
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_HOST, "Eufy Hub"),
                data=user_input,
            )

        # --- Form schema -----------------------------------------------
        # vol.Required fields must be filled; vol.Optional fields have
        # defaults. The poll_interval is coerced to int and clamped 10-300.
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(
                    CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
