"""Tests for the Eufy Sensor platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT

from custom_components.eufy_custom_integration.sensor import (
    EufyBatterySensor,
    EufyWiFiSignalSensor,
)


async def test_battery_sensor_initialization(mock_coordinator: MagicMock) -> None:
    """Test battery sensor initialization."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyBatterySensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera Battery Level"
    assert sensor.unique_id == "SN123456789_Battery Level"
    assert sensor.device_class == SensorDeviceClass.BATTERY
    assert sensor.native_unit_of_measurement == PERCENTAGE


async def test_battery_sensor_value(mock_coordinator: MagicMock) -> None:
    """Test battery sensor value."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyBatterySensor(mock_coordinator, "camera_1", device_info)

    assert sensor.native_value == 85


async def test_battery_sensor_value_none(mock_coordinator: MagicMock) -> None:
    """Test battery sensor value when no data."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyBatterySensor(mock_coordinator, "camera_1", device_info)

    mock_coordinator.data = None
    assert sensor.native_value is None


async def test_wifi_signal_sensor_initialization(
    mock_coordinator: MagicMock,
) -> None:
    """Test WiFi signal sensor initialization."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyWiFiSignalSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.name == "Front Door Camera WiFi Signal"
    assert sensor.unique_id == "SN123456789_WiFi Signal"
    assert sensor.device_class == SensorDeviceClass.SIGNAL_STRENGTH
    assert sensor.native_unit_of_measurement == SIGNAL_STRENGTH_DECIBELS_MILLIWATT


async def test_wifi_signal_sensor_value(mock_coordinator: MagicMock) -> None:
    """Test WiFi signal sensor value."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyWiFiSignalSensor(mock_coordinator, "camera_1", device_info)

    assert sensor.native_value == -45


async def test_sensor_availability(mock_coordinator: MagicMock) -> None:
    """Test sensor availability."""
    device_info = mock_coordinator.data["camera_1"]
    sensor = EufyBatterySensor(mock_coordinator, "camera_1", device_info)

    assert sensor.available is True
