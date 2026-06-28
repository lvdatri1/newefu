"""
Tests for the Eufy Device Manager (device_manager.py).

================================================================================
 COVERAGE
================================================================================

 - Device manager initialisation (hass, coordinator reference)
 - async_register_device creates device registry entry with correct fields
   - identifiers, name, model, manufacturer, serial_number
 - get_device returns registered device or None for unknown
 - get_all_devices returns all registered devices
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from homeassistant.helpers import device_registry as dr

from custom_components.eufy_custom_integration.device_manager import (
    EufyDeviceManager,
)
from custom_components.eufy_custom_integration.const import DOMAIN


async def test_device_manager_initialization(
    mock_hass: MagicMock, mock_coordinator: MagicMock
) -> None:
    """Verify device manager stores references to hass and coordinator."""
    manager = EufyDeviceManager(mock_hass, mock_coordinator)

    assert manager.hass == mock_hass
    assert manager.coordinator == mock_coordinator
    assert manager.devices == {}


async def test_device_manager_register_device(
    mock_hass: MagicMock, mock_coordinator: MagicMock
) -> None:
    """Verify async_register_device creates a device registry entry.

    Checks that async_get_or_create is called with the correct
    identifiers, name, model, manufacturer, and serial_number.
    """
    mock_device_registry = MagicMock()
    mock_device_entry = MagicMock()
    mock_device_registry.async_get_or_create.return_value = mock_device_entry

    with patch(
        "homeassistant.helpers.device_registry.async_get",
        return_value=mock_device_registry,
    ):
        manager = EufyDeviceManager(mock_hass, mock_coordinator)
        device_info = mock_coordinator.data["camera_1"]
        result = await manager.async_register_device("camera_1", device_info)

        assert result == mock_device_entry
        assert "camera_1" in manager.devices

        mock_device_registry.async_get_or_create.assert_called_once_with(
            config_entry_id=mock_coordinator.entry.entry_id,
            identifiers={(DOMAIN, "camera_1")},
            name="Front Door Camera",
            model="T8111",
            manufacturer="Eufy",
            sw_version=None,
            serial_number="SN123456789",
        )


async def test_device_manager_get_device(
    mock_hass: MagicMock, mock_coordinator: MagicMock
) -> None:
    """Verify get_device returns the device or None if unknown."""
    mock_device_registry = MagicMock()
    mock_device_registry.async_get_or_create.return_value = MagicMock()

    with patch(
        "homeassistant.helpers.device_registry.async_get",
        return_value=mock_device_registry,
    ):
        manager = EufyDeviceManager(mock_hass, mock_coordinator)
        device_info = mock_coordinator.data["camera_1"]
        await manager.async_register_device("camera_1", device_info)

        device = manager.get_device("camera_1")
        assert device is not None
        assert device["device_info"] == device_info

        unknown = manager.get_device("unknown")
        assert unknown is None


async def test_device_manager_get_all_devices(
    mock_hass: MagicMock, mock_coordinator: MagicMock
) -> None:
    """Verify get_all_devices returns all registered devices."""
    mock_device_registry = MagicMock()
    mock_device_registry.async_get_or_create.return_value = MagicMock()

    with patch(
        "homeassistant.helpers.device_registry.async_get",
        return_value=mock_device_registry,
    ):
        manager = EufyDeviceManager(mock_hass, mock_coordinator)
        for device_id, device_info in mock_coordinator.data.items():
            await manager.async_register_device(device_id, device_info)

        all_devices = manager.get_all_devices()
        assert len(all_devices) == 4
        assert "camera_1" in all_devices
        assert "doorbell_1" in all_devices
        assert "ground_base_1" in all_devices
        assert "lock_1" in all_devices
