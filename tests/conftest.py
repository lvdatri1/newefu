"""Fixtures for Eufy Custom Integration tests."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.eufy_custom_integration.const import DOMAIN

MOCK_DEVICE_DATA: dict[str, Any] = {
    "camera_1": {
        "device_id": "camera_1",
        "device_name": "Front Door Camera",
        "device_model": "T8111",
        "serial_number": "SN123456789",
        "battery_level": 85,
        "wifi_signal": -45,
        "is_online": True,
        "state": "idle",
        "stream_url": "rtsp://192.168.1.100:554/stream1",
        "last_event": None,
        "type": "camera",
        "properties": {
            "night_vision": True,
            "two_way_audio": True,
            "motion_detection": False,
            "motion_detected": False,
        },
    },
    "doorbell_1": {
        "device_id": "doorbell_1",
        "device_name": "Front Doorbell",
        "device_model": "T8200",
        "serial_number": "SN987654321",
        "battery_level": 72,
        "wifi_signal": -50,
        "is_online": True,
        "state": "idle",
        "stream_url": "rtsp://192.168.1.101:554/stream1",
        "last_event": None,
        "type": "doorbell",
        "properties": {
            "night_vision": True,
            "two_way_audio": True,
            "ringing": False,
            "motion_detection": True,
            "motion_detected": False,
        },
    },
    "ground_base_1": {
        "device_id": "ground_base_1",
        "device_name": "HomeBase",
        "device_model": "T8000",
        "serial_number": "SN456789123",
        "is_online": True,
        "state": "disarmed",
        "last_event": None,
        "type": "ground_base",
        "properties": {
            "armed": False,
            "mode": "disarmed",
            "schedule_enabled": False,
        },
    },
    "lock_1": {
        "device_id": "lock_1",
        "device_name": "Front Door Lock",
        "device_model": "T8500",
        "serial_number": "SN555555555",
        "battery_level": 90,
        "wifi_signal": -60,
        "is_online": True,
        "state": "locked",
        "type": "smart_lock",
        "properties": {
            "locked": True,
            "locking": False,
            "unlocking": False,
            "jammed": False,
        },
    },
}


@pytest.fixture
def mock_device_data() -> dict[str, Any]:
    """Return mock device data."""
    return MOCK_DEVICE_DATA


@pytest.fixture
def mock_coordinator(mock_device_data: dict[str, Any]) -> MagicMock:
    """Create a mock coordinator."""
    coordinator = MagicMock()
    coordinator.data = mock_device_data
    coordinator.async_set_updated_data = AsyncMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_config_entry() -> MagicMock:
    """Create a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "host": "192.168.1.1",
        "port": 5222,
        "username": "test_user",
        "password": "test_password",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    hass.config = MagicMock()
    return hass
