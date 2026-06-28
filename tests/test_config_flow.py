"""Config flow tests for the Eufy Custom Integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant import config_entries, data_entry_flow

from custom_components.eufy_custom_integration.config_flow import EufyConfigFlow
from custom_components.eufy_custom_integration.const import DOMAIN


async def test_config_flow_user_step(mock_hass: MagicMock) -> None:
    """Test config flow user step."""
    flow = EufyConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user()
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_config_flow_user_step_create_entry(
    mock_hass: MagicMock,
) -> None:
    """Test config flow user step with data."""
    flow = EufyConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_user(
        user_input={
            "host": "192.168.1.1",
            "username": "test",
            "password": "test",
            "port": 5222,
            "poll_interval": 30,
        }
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "192.168.1.1"
    assert result["data"]["host"] == "192.168.1.1"
    assert result["data"]["username"] == "test"


async def test_config_flow_domain(mock_hass: MagicMock) -> None:
    """Test config flow domain."""
    flow = EufyConfigFlow()
    assert flow.domain == DOMAIN


async def test_config_flow_version(mock_hass: MagicMock) -> None:
    """Test config flow version."""
    flow = EufyConfigFlow()
    assert flow.VERSION == 1
