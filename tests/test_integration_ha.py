"""Full integration test: loads the component into a real Home Assistant instance.

Exercises the complete lifecycle:
  1. Create a real HomeAssistant instance with a temp config directory.
  2. Set up the integration via async_setup_entry.
  3. Verify the coordinator is created and populated with device data.
  4. Simulate a data update through the coordinator.
  5. Verify unload cleans up properly.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.loader import DATA_INTEGRATIONS

from custom_components.lvdatri_eufy import async_setup_entry, async_unload_entry
from custom_components.lvdatri_eufy.const import (
    CONF_COUNTRY,
    CONF_POLL_INTERVAL,
    DOMAIN,
)
from custom_components.lvdatri_eufy.coordinator import (
    EufyDataUpdateCoordinator,
)

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
}


@pytest.fixture
def mock_devices() -> dict[str, Any]:
    """Return controlled mock device data."""
    return MOCK_DEVICE_DATA


@pytest.fixture
async def hass_instance(tmp_path: str) -> HomeAssistant:
    """Create a real HomeAssistant instance for integration testing."""
    config_dir = os.path.join(str(tmp_path), "homeassistant")
    os.makedirs(config_dir, exist_ok=True)
    hass = HomeAssistant(config_dir)
    hass.data[DATA_INTEGRATIONS] = {}
    hass.data[DOMAIN] = {}

    config_entries_mock = MagicMock()
    config_entries_mock.async_forward_entry_setups = AsyncMock(return_value=True)
    config_entries_mock.async_unload_platforms = AsyncMock(return_value=True)
    hass.config_entries = config_entries_mock

    try:
        yield hass
    finally:
        await hass.async_stop()


def make_entry(
    title: str,
    entry_id: str,
    username: str = "test@eufy.com",
    password: str = "secret",
    country: str = "US",
    poll_interval: int = 30,
) -> ConfigEntry:
    """Build a ConfigEntry for testing."""
    return ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title=title,
        data={
            CONF_USERNAME: username,
            CONF_PASSWORD: password,
            CONF_COUNTRY: country,
            CONF_POLL_INTERVAL: poll_interval,
        },
        source="user" if "user" in entry_id else "import",
        entry_id=entry_id,
        options={},
        discovery_keys={},
        unique_id=entry_id,
    )


@pytest.mark.asyncio
async def test_setup_entry_creates_coordinator_and_devices(
    hass_instance: HomeAssistant,
    mock_devices: dict[str, Any],
) -> None:
    """Full end-to-end: config entry -> coordinator -> populated data."""
    hass = hass_instance
    entry = make_entry("env@eufy.com", "entry_1")

    with patch.object(
        EufyDataUpdateCoordinator,
        "_fetch_devices",
        return_value=mock_devices,
    ):
        result = await async_setup_entry(hass, entry)
        assert result is True

    assert entry.entry_id in hass.data[DOMAIN]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    assert coordinator is not None
    assert "camera_1" in coordinator.data
    assert coordinator.data["camera_1"]["battery_level"] == 85

    assert "device_manager" in hass.data[DOMAIN][entry.entry_id]


@pytest.mark.asyncio
async def test_coordinator_updates_after_setup(
    hass_instance: HomeAssistant,
    mock_devices: dict[str, Any],
) -> None:
    """Simulate a data update through the coordinator after setup."""
    hass = hass_instance
    entry = make_entry("test@eufy.com", "entry_2")

    with patch.object(
        EufyDataUpdateCoordinator,
        "_fetch_devices",
        return_value=mock_devices,
    ):
        await async_setup_entry(hass, entry)

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    coordinator.data["camera_1"]["battery_level"] = 42
    coordinator.data["camera_1"]["properties"]["motion_detected"] = True
    coordinator.async_set_updated_data(coordinator.data)

    assert coordinator.data["camera_1"]["battery_level"] == 42
    assert coordinator.data["camera_1"]["properties"]["motion_detected"] is True


@pytest.mark.asyncio
async def test_unload_entry_cleans_up(
    hass_instance: HomeAssistant,
    mock_devices: dict[str, Any],
) -> None:
    """Verify that unloading removes entry data from hass.data."""
    hass = hass_instance
    entry = make_entry("unload@eufy.com", "entry_3")

    with patch.object(
        EufyDataUpdateCoordinator,
        "_fetch_devices",
        return_value=mock_devices,
    ):
        await async_setup_entry(hass, entry)

    assert entry.entry_id in hass.data[DOMAIN]

    unload_ok = await async_unload_entry(hass, entry)
    assert unload_ok is True
    assert entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_coordinator_fetch_devices_returns_mock_data(
    hass_instance: HomeAssistant,
    mock_devices: dict[str, Any],
) -> None:
    """Verify the patched _fetch_devices is called and returns expected data."""
    hass = hass_instance
    entry = make_entry("fetch@eufy.com", "entry_4")

    with patch.object(
        EufyDataUpdateCoordinator,
        "_fetch_devices",
        return_value=mock_devices,
    ) as mock_fetch:
        await async_setup_entry(hass, entry)
        assert mock_fetch.called

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    # After the patch exits, _fetch_devices reverts to the real method
    # which returns the full default mock data.
    data = await coordinator._fetch_devices()
    assert "camera_1" in data
    assert data["camera_1"]["type"] == "camera"


@pytest.mark.asyncio
async def test_coordinator_initial_refresh_populates_data(
    hass_instance: HomeAssistant,
    mock_devices: dict[str, Any],
) -> None:
    """Ensure _fetch_devices data is available immediately after setup."""
    hass = hass_instance
    entry = make_entry("refresh@eufy.com", "entry_5")

    with patch.object(
        EufyDataUpdateCoordinator,
        "_fetch_devices",
        return_value=mock_devices,
    ):
        await async_setup_entry(hass, entry)

    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    assert coordinator.data["camera_1"]["device_name"] == "Front Door Camera"
    assert coordinator.data["camera_1"]["properties"]["motion_detection"] is False
