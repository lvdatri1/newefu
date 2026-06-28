"""Tests for the Eufy Coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.eufy_custom_integration.coordinator import (
    EufyDataUpdateCoordinator,
)
from custom_components.eufy_custom_integration.const import DOMAIN


async def test_coordinator_initialization(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator initialization."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)

    assert coordinator.name == DOMAIN
    assert coordinator.entry == mock_config_entry


async def test_coordinator_fetch_devices(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator fetch devices."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)

    data = await coordinator._fetch_devices()

    assert "camera_1" in data
    assert "doorbell_1" in data
    assert "ground_base_1" in data

    camera = data["camera_1"]
    assert camera["device_name"] == "Front Door Camera"
    assert camera["type"] == "camera"
    assert camera["battery_level"] == 85
    assert camera["wifi_signal"] == -45
    assert camera["is_online"] is True

    doorbell = data["doorbell_1"]
    assert doorbell["device_name"] == "Front Doorbell"
    assert doorbell["type"] == "doorbell"

    ground_base = data["ground_base_1"]
    assert ground_base["device_name"] == "HomeBase"
    assert ground_base["type"] == "ground_base"
    assert ground_base["state"] == "disarmed"


async def test_coordinator_set_mode(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator set mode."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)
    coordinator.data = await coordinator._fetch_devices()

    with patch.object(coordinator, "async_set_updated_data") as mock_set:
        result = await coordinator.set_mode("ground_base_1", "away")
        assert result is True
        assert coordinator.data["ground_base_1"]["properties"]["mode"] == "away"
        mock_set.assert_called_once()


async def test_coordinator_set_mode_invalid_device(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator set mode with invalid device."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)
    coordinator.data = await coordinator._fetch_devices()

    result = await coordinator.set_mode("invalid_device", "away")
    assert result is False


async def test_coordinator_trigger_alarm(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator trigger alarm."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)
    coordinator.data = await coordinator._fetch_devices()

    with patch.object(coordinator, "async_set_updated_data") as mock_set:
        result = await coordinator.trigger_alarm("ground_base_1")
        assert result is True
        assert coordinator.data["ground_base_1"]["state"] == "alarm_triggered"
        mock_set.assert_called_once()


async def test_coordinator_disarm_alarm(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> None:
    """Test coordinator disarm alarm."""
    coordinator = EufyDataUpdateCoordinator(mock_hass, mock_config_entry)
    coordinator.data = await coordinator._fetch_devices()
    coordinator.data["ground_base_1"]["state"] = "alarm_triggered"

    with patch.object(coordinator, "async_set_updated_data") as mock_set:
        result = await coordinator.disarm_alarm("ground_base_1")
        assert result is True
        assert coordinator.data["ground_base_1"]["state"] == "disarmed"
        mock_set.assert_called_once()
