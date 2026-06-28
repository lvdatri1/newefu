"""
Tests for the Eufy Binary Sensor platform (binary_sensor.py).

================================================================================
 COVERAGE
================================================================================

 - Motion sensor initialisation and device_class
 - Motion sensor is_on returns False when no motion
 - Motion sensor is_on returns True when motion detected
 - Online sensor initialisation and device_class
 - Online sensor is_on returns True when device is online
 - Online sensor is_on returns False when device is offline
 - Doorbell press sensor initialisation and device_class
 - Doorbell press sensor is_on returns False when not ringing
 - Doorbell press sensor is_on returns True when ringing
"""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.lvdatri_eufy.binary_sensor import (
    EufyDoorbellPressSensor,
    EufyMotionSensor,
    EufyOnlineSensor,
)


async def test_motion_sensor_initialization(mock_coordinator: MagicMock) -> None:
    """Verify motion sensor is created with correct metadata and device class."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera Motion"
    assert sensor.unique_id == "SN123456789_Motion"
    assert sensor.device_class == BinarySensorDeviceClass.MOTION


async def test_motion_sensor_no_motion(mock_coordinator: MagicMock) -> None:
    """Verify is_on is False when properties.motion_detected is False."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is False


async def test_motion_sensor_motion_detected(mock_coordinator: MagicMock) -> None:
    """Verify is_on is True when properties.motion_detected is True."""
    mock_coordinator.data["camera_1"]["properties"]["motion_detected"] = True
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyMotionSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is True


async def test_online_sensor_initialization(mock_coordinator: MagicMock) -> None:
    """Verify online sensor is created with correct metadata."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera Online"
    assert sensor.unique_id == "SN123456789_Online"
    assert sensor.device_class == BinarySensorDeviceClass.CONNECTIVITY


async def test_online_sensor_is_online(mock_coordinator: MagicMock) -> None:
    """Verify is_on is True when device is_online is True."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is True


async def test_online_sensor_is_offline(mock_coordinator: MagicMock) -> None:
    """Verify is_on is False when device is_online is False."""
    mock_coordinator.data["camera_1"]["is_online"] = False
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyOnlineSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.is_on is False


async def test_doorbell_press_sensor_initialization(
    mock_coordinator: MagicMock,
) -> None:
    """Verify doorbell press sensor is created with correct metadata."""
    device_info = mock_coordinator.data["doorbell_1"]
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.name == "Front Doorbell Ring"
    assert sensor.unique_id == "SN987654321_Ring"
    assert sensor.device_class == BinarySensorDeviceClass.OCCUPANCY


async def test_doorbell_not_ringing(mock_coordinator: MagicMock) -> None:
    """Verify is_on is False when properties.ringing is False."""
    device_info = mock_coordinator.data["doorbell_1"]
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.is_on is False


async def test_doorbell_ringing(mock_coordinator: MagicMock) -> None:
    """Verify is_on is True when properties.ringing is True."""
    mock_coordinator.data["doorbell_1"]["properties"]["ringing"] = True
    device_info = mock_coordinator.data["doorbell_1"]
    sensor = EufyDoorbellPressSensor(mock_coordinator, "doorbell_1", device_info)

    assert sensor.is_on is True
