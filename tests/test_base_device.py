"""
Tests for the Eufy Base Device Entity (devices/base_device.py).

================================================================================
 COVERAGE
================================================================================

 - Base device entity initialisation (name, unique_id, device_info)
 - Base device entity with entity_type suffix in name/unique_id
 - Entity availability when coordinator has data
 - Entity unavailability when coordinator data is None
 - Entity unavailability when device_id is missing from data
 - _get_device_data() returns device data dict
 - _get_device_data() returns None when device_id is unknown
 - _get_property() reads from properties dict
 - _get_property() returns default when key is missing
"""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lvdatri_eufy.devices.base_device import (
    EufyDeviceEntity,
)
from custom_components.lvdatri_eufy.const import DOMAIN


async def test_base_device_initialization(mock_coordinator: MagicMock) -> None:
    """Verify base device entity is created with correct metadata."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    assert entity.name == "Front Door Camera"
    assert entity.unique_id == "SN123456789"
    assert entity._attr_device_info["manufacturer"] == "Eufy"
    assert entity._attr_device_info["model"] == "T8111"


async def test_base_device_with_entity_type(
    mock_coordinator: MagicMock,
) -> None:
    """Verify entity_type suffix is appended to name and unique_id."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "camera_1", device_info, "Battery"
    )

    assert entity.name == "Front Door Camera Battery"
    assert entity.unique_id == "SN123456789_Battery"


async def test_base_device_available(mock_coordinator: MagicMock) -> None:
    """Verify entity is available when coordinator has valid data."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    assert entity.available is True

    mock_coordinator.data = None
    assert entity.available is False


async def test_base_device_not_available_when_missing(
    mock_coordinator: MagicMock,
) -> None:
    """Verify entity is unavailable when device_id is not in data."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "missing_device", device_info
    )

    assert entity.available is False


async def test_get_device_data(mock_coordinator: MagicMock) -> None:
    """Verify _get_device_data() returns the full device data dict."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    data = entity._get_device_data()
    assert data == mock_coordinator.data["camera_1"]


async def test_get_device_data_none(mock_coordinator: MagicMock) -> None:
    """Verify _get_device_data() returns None for unknown device_id."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "missing_device", device_info
    )

    data = entity._get_device_data()
    assert data is None


async def test_get_property(mock_coordinator: MagicMock) -> None:
    """Verify _get_property() reads values from the properties dict."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    value = entity._get_property("night_vision")
    assert value is True


async def test_get_property_default(mock_coordinator: MagicMock) -> None:
    """Verify _get_property() returns the default when key is missing."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    value = entity._get_property("nonexistent", "default_val")
    assert value == "default_val"
