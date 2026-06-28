"""
Config flow for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 The config flow handles the UI-based setup wizard that users follow when
 adding "Eufy Custom Integration" via Settings -> Devices & Services.
 It collects Eufy account credentials (username, password, country code)
 and creates a ConfigEntry that persists these settings.

 Eufy uses cloud-based authentication — email, password, and a country
 code are needed to determine the correct regional API server.
 No local hub IP or port is required.

================================================================================
 STEPS
================================================================================

 1. user:        The initial form. Collects username, password, country
                 code, and poll interval. On submit, creates the config entry.

 FUTURE STEPS (to implement):
   - async_step_reauth:    Handle credential expiry / 2FA challenge.
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
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_COUNTRY,
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)

# Common Eufy country codes for the dropdown selector.
# These map to Eufy's regional API servers.
COUNTRY_OPTIONS = [
    selector.SelectOptionDict(value="US", label="United States"),
    selector.SelectOptionDict(value="GB", label="United Kingdom"),
    selector.SelectOptionDict(value="DE", label="Germany"),
    selector.SelectOptionDict(value="FR", label="France"),
    selector.SelectOptionDict(value="NL", label="Netherlands"),
    selector.SelectOptionDict(value="AU", label="Australia"),
    selector.SelectOptionDict(value="CA", label="Canada"),
    selector.SelectOptionDict(value="IT", label="Italy"),
    selector.SelectOptionDict(value="ES", label="Spain"),
    selector.SelectOptionDict(value="BE", label="Belgium"),
    selector.SelectOptionDict(value="CH", label="Switzerland"),
    selector.SelectOptionDict(value="AT", label="Austria"),
    selector.SelectOptionDict(value="SE", label="Sweden"),
    selector.SelectOptionDict(value="NO", label="Norway"),
    selector.SelectOptionDict(value="DK", label="Denmark"),
    selector.SelectOptionDict(value="JP", label="Japan"),
    selector.SelectOptionDict(value="CN", label="China"),
]


class EufyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eufy Custom Integration.

    This is the UI workflow that runs when a user clicks "Add Integration"
    in Home Assistant. It presents a form, validates input, and creates
    a ConfigEntry that persists the Eufy cloud account credentials.

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
          - username (required):           Eufy account email
          - password (required):           Eufy account password
          - country (required):            2-letter ISO country code
          - poll_interval (optional, 30s): How often to poll the API

        The country code is needed by Eufy's API to route requests
        to the correct regional server for your account.

        Args:
            user_input: Dict of user-provided values, or None to show form.

        Returns:
            A FlowResult (either the form to display, or a created entry).
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_USERNAME, "Eufy Account"),
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_COUNTRY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=COUNTRY_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
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
