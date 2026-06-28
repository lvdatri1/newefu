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

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant import config_entries, data_entry_flow

from custom_components.lvdatri_eufy.config_flow import EufyConfigFlow
from custom_components.lvdatri_eufy.const import DOMAIN


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
    """Verify the config flow title matches the username when provided."""
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


async def test_env_var_auto_setup(mock_hass: MagicMock) -> None:
    """Verify async_setup auto-creates entry when env vars are set."""
    mock_hass.config_entries.async_entries.return_value = []

    create_task_calls: list = []

    def fake_create_task(coro: Any) -> None:
        create_task_calls.append(coro)

    mock_hass.async_create_task = fake_create_task

    with patch("custom_components.lvdatri_eufy.os.environ", {
        "EUFY_USERNAME": "env@eufy.com",
        "EUFY_PASSWORD": "secret",
        "EUFY_COUNTRY": "GB",
    }):
        from custom_components.lvdatri_eufy import async_setup
        result = await async_setup(mock_hass, {})

    assert result is True
    assert len(create_task_calls) == 1


async def test_env_var_auto_setup_skips_when_entry_exists(
    mock_hass: MagicMock,
) -> None:
    """Verify async_setup does NOT auto-create entry if one already exists."""
    mock_hass.config_entries.async_entries.return_value = ["existing_entry"]
    mock_hass.async_create_task = MagicMock()

    with patch("custom_components.lvdatri_eufy.os.environ", {
        "EUFY_USERNAME": "env@eufy.com",
        "EUFY_PASSWORD": "secret",
        "EUFY_COUNTRY": "GB",
    }):
        from custom_components.lvdatri_eufy import async_setup
        result = await async_setup(mock_hass, {})

    assert result is True
    mock_hass.async_create_task.assert_not_called()


async def test_env_var_auto_setup_skips_when_vars_missing(
    mock_hass: MagicMock,
) -> None:
    """Verify async_setup does nothing when env vars are not set."""
    mock_hass.config_entries.async_entries.return_value = []
    mock_hass.async_create_task = MagicMock()

    with patch("custom_components.lvdatri_eufy.os.environ", {}):
        from custom_components.lvdatri_eufy import async_setup
        result = await async_setup(mock_hass, {})

    assert result is True
    mock_hass.async_create_task.assert_not_called()


async def test_config_flow_import(mock_hass: MagicMock) -> None:
    """Verify the import step creates an entry from env-var-style data."""
    flow = EufyConfigFlow()
    flow.hass = mock_hass

    result = await flow.async_step_import(
        user_input={
            "username": "env@eufy.com",
            "password": "env_pass",
            "country": "DE",
        }
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "env@eufy.com"
    assert result["data"]["username"] == "env@eufy.com"
    assert result["data"]["country"] == "DE"


async def test_config_flow_version(mock_hass: MagicMock) -> None:
    """Verify the config flow version is 1."""
    flow = EufyConfigFlow()
    assert flow.VERSION == 1
