"""Tests for the Eufy Base Device Entity."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.devices.base_device import (
    EufyDeviceEntity,
)
from custom_components.eufy_custom_integration.const import DOMAIN


async def test_base_device_initialization(mock_coordinator: MagicMock) -> None:
    """Test base device entity initialization."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    assert entity.name == "Front Door Camera"
    assert entity.unique_id == "SN123456789"
    assert entity._attr_device_info["manufacturer"] == "Eufy"
    assert entity._attr_device_info["model"] == "T8111"


async def test_base_device_with_entity_type(
    mock_coordinator: MagicMock,
) -> None:
    """Test base device entity initialization with entity type."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "camera_1", device_info, "Battery"
    )

    assert entity.name == "Front Door Camera Battery"
    assert entity.unique_id == "SN123456789_Battery"


async def test_base_device_available(mock_coordinator: MagicMock) -> None:
    """Test base device entity availability."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    assert entity.available is True

    mock_coordinator.data = None
    assert entity.available is False


async def test_base_device_not_available_when_missing(
    mock_coordinator: MagicMock,
) -> None:
    """Test base device entity not available when missing from data."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "missing_device", device_info
    )

    assert entity.available is False


async def test_get_device_data(mock_coordinator: MagicMock) -> None:
    """Test _get_device_data method."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    data = entity._get_device_data()
    assert data == mock_coordinator.data["camera_1"]


async def test_get_device_data_none(mock_coordinator: MagicMock) -> None:
    """Test _get_device_data returns None when no data."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(
        mock_coordinator, "missing_device", device_info
    )

    data = entity._get_device_data()
    assert data is None


async def test_get_property(mock_coordinator: MagicMock) -> None:
    """Test _get_property method."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    value = entity._get_property("night_vision")
    assert value is True


async def test_get_property_default(mock_coordinator: MagicMock) -> None:
    """Test _get_property returns default."""
    device_info = mock_coordinator.data["camera_1"]
    entity = EufyDeviceEntity(mock_coordinator, "camera_1", device_info)

    value = entity._get_property("nonexistent", "default_val")
    assert value == "default_val"
