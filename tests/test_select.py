"""
Tests for the Eufy Select platform (select.py).

================================================================================
 COVERAGE
================================================================================

 - Mode selector initialisation (name, unique_id)
 - Available options list matches expected security modes
 - Current option reads from properties.mode
 - Selecting a valid option updates state and notifies HA
 - Selecting an invalid option does not change state
"""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.select import (
    AVAILABLE_MODES,
    EufyModeSelect,
)


async def test_select_initialization(mock_coordinator: MagicMock) -> None:
    """Verify mode selector entity is created with correct metadata."""
    device_info = mock_coordinator.data["ground_base_1"]
    select = EufyModeSelect(mock_coordinator, "ground_base_1", device_info)

    assert select.name == "HomeBase Security Mode"
    assert select.unique_id == "SN456789123_Security Mode"


async def test_select_options(mock_coordinator: MagicMock) -> None:
    """Verify the available options match the full security mode list."""
    device_info = mock_coordinator.data["ground_base_1"]
    select = EufyModeSelect(mock_coordinator, "ground_base_1", device_info)

    assert select.options == AVAILABLE_MODES


async def test_select_current_option(mock_coordinator: MagicMock) -> None:
    """Verify current_option returns the mode from device properties."""
    device_info = mock_coordinator.data["ground_base_1"]
    select = EufyModeSelect(mock_coordinator, "ground_base_1", device_info)

    assert select.current_option == "disarmed"


async def test_select_select_option(mock_coordinator: MagicMock) -> None:
    """Verify selecting a valid option updates state and triggers HA update."""
    device_info = mock_coordinator.data["ground_base_1"]
    select = EufyModeSelect(mock_coordinator, "ground_base_1", device_info)

    await select.async_select_option("away")
    assert select.current_option == "away"
    mock_coordinator.async_set_updated_data.assert_called_once()


async def test_select_select_invalid_option(
    mock_coordinator: MagicMock,
) -> None:
    """Verify selecting an invalid option does not change the mode."""
    device_info = mock_coordinator.data["ground_base_1"]
    select = EufyModeSelect(mock_coordinator, "ground_base_1", device_info)

    initial = select.current_option
    await select.async_select_option("invalid_mode")
    assert select.current_option == initial
