"""
Tests for the Eufy Config Flow (config_flow.py).

================================================================================
 COVERAGE
================================================================================

 - Config flow user step shows form with expected step_id
 - Config flow user step creates entry with provided data
 - Config flow domain matches DOMAIN constant
 - Config flow version is correct
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant import config_entries, data_entry_flow

from custom_components.eufy_custom_integration.config_flow import EufyConfigFlow
from custom_components.eufy_custom_integration.const import DOMAIN


async def test_config_flow_user_step(mock_hass: MagicMock) -> None:
    """Verify the user step shows a form with the correct step_id."""
    flow = EufyConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_config_flow_user_step_create_entry(
    mock_hass: MagicMock,
) -> None:
    """Verify submitting user data creates a config entry."""
    flow = EufyConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user(
        user_input={
            "username": "test@eufy.com",
            "password": "test",
            "country": "US",
            "poll_interval": 30,
        }
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "test@eufy.com"
    assert result["data"]["username"] == "test@eufy.com"
    assert result["data"]["country"] == "US"


async def test_config_flow_domain(mock_hass: MagicMock) -> None:
    """Verify the config flow domain matches the integration domain."""
    flow = EufyConfigFlow()
    assert flow.domain == DOMAIN


async def test_config_flow_version(mock_hass: MagicMock) -> None:
    """Verify the config flow version is 1."""
    flow = EufyConfigFlow()
    assert flow.VERSION == 1
