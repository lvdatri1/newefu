"""Tests for the Eufy Binary Sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.eufy_custom_integration.binary_sensor import (
    EufyDoorbellPressSensor,
    EufyMotionSensor,
    EufyOnlineSensor,
)


async def test_motion_sensor_initialization(mock_coordinator: MagicMock) -> None:
    """Test motion sensor initialization."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera Motion"
    assert sensor.unique_id == "SN123456789_Motion"
    assert sensor.device_class == BinarySensorDeviceClass.MOTION


async def test_motion_sensor_no_motion(mock_coordinator: MagicMock) -> None:
    """Test motion sensor no motion."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is False


async def test_motion_sensor_motion_detected(mock_coordinator: MagicMock) -> None:
    """Test motion sensor motion detected."""
    device_info = dict(mock_coordinator.data["camera_1"])
    device_info["properties"] = {"motion_detected": True}
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is True


async def test_online_sensor_initialization(mock_coordinator: MagicMock) -> None:
    """Test online sensor initialization."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera Online"
    assert sensor.unique_id == "SN123456789_Online"
    assert sensor.device_class == BinarySensorDeviceClass.CONNECTIVITY


async def test_online_sensor_is_online(mock_coordinator: MagicMock) -> None:
    """Test online sensor when device is online."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is True


async def test_online_sensor_is_offline(mock_coordinator: MagicMock) -> None:
    """Test online sensor when device is offline."""
    device_info = dict(mock_coordinator.data["camera_1"])
    device_info["is_online"] = False
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is False


async def test_doorbell_press_sensor_initialization(
    mock_coordinator: MagicMock,
) -> None:
    """Test doorbell press sensor initialization."""
    device_info = mock_coordinator.data["doorbell_1"]
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.name == "Front Doorbell Ring"
    assert sensor.unique_id == "SN987654321_Ring"
    assert sensor.device_class == BinarySensorDeviceClass.OCCUPANCY


async def test_doorbell_not_ringing(mock_coordinator: MagicMock) -> None:
    """Test doorbell not ringing."""
    device_info = mock_coordinator.data["doorbell_1"]
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.is_on is False


async def test_doorbell_ringing(mock_coordinator: MagicMock) -> None:
    """Test doorbell ringing."""
    device_info = dict(mock_coordinator.data["doorbell_1"])
    device_info["properties"] = {"ringing": True}
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.is_on is True
