"""
Tests for the Eufy Switch platform (switch.py).

================================================================================
 COVERAGE
================================================================================

 - Motion detection switch initialisation (name, unique_id)
 - Switch is off when motion_detection property is False
 - Switch turns on (sets motion_detection = True)
 - Switch turns off (sets motion_detection = False)
 - Switch availability when coordinator has data
"""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.switch import EufyMotionDetectionSwitch


async def test_switch_initialization(mock_coordinator: MagicMock) -> None:
    """Verify switch entity is created with correct metadata."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.name == "Front Door Camera Motion Detection"
    assert switch.unique_id == "SN123456789_Motion Detection"


async def test_switch_is_off(mock_coordinator: MagicMock) -> None:
    """Verify switch is off when motion_detection is False in properties."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.is_on is False


async def test_switch_turn_on(mock_coordinator: MagicMock) -> None:
    """Verify async_turn_on sets motion_detection to True and notifies HA."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    await switch.async_turn_on()
    assert switch.is_on is True
    mock_coordinator.async_set_updated_data.assert_called_once()


async def test_switch_turn_off(mock_coordinator: MagicMock) -> None:
    """Verify async_turn_off sets motion_detection to False and notifies HA."""
    mock_coordinator.data["camera_1"]["properties"]["motion_detection"] = True
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.is_on is True

    await switch.async_turn_off()
    assert switch.is_on is False


async def test_switch_availability(mock_coordinator: MagicMock) -> None:
    """Verify switch is available when coordinator has valid data."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.available is True
