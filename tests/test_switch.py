"""Tests for the Eufy Switch platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.switch import EufyMotionDetectionSwitch


async def test_switch_initialization(mock_coordinator: MagicMock) -> None:
    """Test switch initialization."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.name == "Front Door Camera Motion Detection"
    assert switch.unique_id == "SN123456789_Motion Detection"


async def test_switch_is_off(mock_coordinator: MagicMock) -> None:
    """Test switch off state."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.is_on is False


async def test_switch_turn_on(mock_coordinator: MagicMock) -> None:
    """Test switch turn on."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    await switch.async_turn_on()
    assert switch.is_on is True
    mock_coordinator.async_set_updated_data.assert_called_once()


async def test_switch_turn_off(mock_coordinator: MagicMock) -> None:
    """Test switch turn off."""
    device_info = dict(mock_coordinator.data["camera_1"])
    device_info["properties"] = {"motion_detection": True}
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.is_on is True

    await switch.async_turn_off()
    assert switch.is_on is False


async def test_switch_availability(mock_coordinator: MagicMock) -> None:
    """Test switch availability."""
    device_info = mock_coordinator.data["camera_1"]
    switch = EufyMotionDetectionSwitch(mock_coordinator, "camera_1", device_info)

    assert switch.available is True
