"""Tests for the Eufy Button platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.button import EufyWakeUpButton


async def test_button_initialization(mock_coordinator: MagicMock) -> None:
    """Test button initialization."""
    device_info = mock_coordinator.data["camera_1"]
    button = EufyWakeUpButton(mock_coordinator, "camera_1", device_info)

    assert button.name == "Front Door Camera Wake Up"
    assert button.unique_id == "SN123456789_Wake Up"


async def test_button_press(mock_coordinator: MagicMock) -> None:
    """Test button press."""
    device_info = mock_coordinator.data["camera_1"]
    button = EufyWakeUpButton(mock_coordinator, "camera_1", device_info)

    await button.async_press()
    assert mock_coordinator.data["camera_1"]["state"] == "waking"
    mock_coordinator.async_set_updated_data.assert_called_once()
