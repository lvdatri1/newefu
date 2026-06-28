"""
Test fixtures and helpers for the Eufy Custom Integration.

================================================================================
 USAGE
================================================================================

 Run tests with mock data (default):
     pytest tests/ -v

 Run tests against a real Eufy account (integration tests):
     export EUFY_USERNAME="your@email.com"
     export EUFY_PASSWORD="your_password"
     pytest tests/ -v --run-real

 When env vars are set, conftest.py will create a real coordinator
 that connects to the Eufy cloud API. Otherwise, all fixtures return
 Mock objects with the sample device data defined in MOCK_DEVICE_DATA.

 Note: Eufy uses cloud authentication — only email + password needed,
 no hub IP or port required.

================================================================================
 FIXTURES
================================================================================

 mock_device_data     -- Dict of 4 simulated Eufy devices (camera, doorbell,
                         ground_base, lock) with realistic properties.

 mock_coordinator     -- MagicMock that mimics EufyDataUpdateCoordinator,
                         pre-populated with mock_device_data.

 mock_config_entry    -- MagicMock representing a saved HA ConfigEntry.

 mock_hass            -- MagicMock representing a HomeAssistant instance.

 eufy_username        -- The Eufy account email (from env or "test_user").
 eufy_password        -- The Eufy account password (from env or "test_password").

================================================================================
 REAL DEVICE TESTING
================================================================================

 To run integration tests against your actual Eufy account:

 1. Set the environment variables listed above.
 2. Run:  pytest tests/ -v --run-real

 This will skip tests that require mocked coordinators and instead
 execute tests that connect to the real Eufy cloud API.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.eufy_custom_integration.const import DOMAIN

# -----------------------------------------------------------------------
# CREDENTIALS (from environment variables)
# Eufy uses cloud authentication — only email + password needed.
# No hub IP or port required.
# -----------------------------------------------------------------------

EUFY_USERNAME: str | None = os.environ.get("EUFY_USERNAME")
EUFY_PASSWORD: str | None = os.environ.get("EUFY_PASSWORD")
EUFY_COUNTRY: str | None = os.environ.get("EUFY_COUNTRY")

# True if the user has provided real Eufy credentials via env vars.
HAVE_REAL_CREDENTIALS: bool = bool(EUFY_USERNAME and EUFY_PASSWORD and EUFY_COUNTRY)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom pytest CLI options.

    --run-real:  Run tests that connect to a real Eufy account.
                 Requires EUFY_USERNAME / EUFY_PASSWORD env vars.
    """
    parser.addoption(
        "--run-real",
        action="store_true",
        default=False,
        help="Run integration tests against a real Eufy account",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip real-device tests unless --run-real is passed.

    Tests marked with @pytest.mark.real_device will be skipped unless
    the --run-real flag is provided AND EUFY_USERNAME/EUFY_PASSWORD/
    EUFY_COUNTRY env vars are set.
    """
    if not config.getoption("--run-real") or not HAVE_REAL_CREDENTIALS:
        skip_real = pytest.mark.skip(
            reason="Requires --run-real flag and EUFY_USERNAME/"
            "EUFY_PASSWORD/EUFY_COUNTRY env vars"
        )
        for item in items:
            if "real_device" in item.keywords:
                item.add_marker(skip_real)
    elif not HAVE_REAL_CREDENTIALS:
        skip_real = pytest.mark.skip(
            reason="Missing EUFY_USERNAME/EUFY_PASSWORD/EUFY_COUNTRY env vars"
        )
        for item in items:
            if "real_device" in item.keywords:
                item.add_marker(skip_real)


# -----------------------------------------------------------------------
# MOCK DEVICE DATA
# These simulate the data returned by coordinator._fetch_devices().
# Each dict matches the expected schema documented in coordinator.py.
# -----------------------------------------------------------------------

MOCK_DEVICE_DATA: dict[str, Any] = {
    "camera_1": {
        "device_id":    "camera_1",
        "device_name":  "Front Door Camera",
        "device_model": "T8111",
        "serial_number": "SN123456789",
        "battery_level": 85,
        "wifi_signal":   -45,
        "is_online":     True,
        "state":         "idle",
        "stream_url":    "rtsp://192.168.1.100:554/stream1",
        "last_event":    None,
        "type":          "camera",
        "properties": {
            "night_vision":     True,
            "two_way_audio":    True,
            "motion_detection": False,
            "motion_detected":  False,
        },
    },
    "doorbell_1": {
        "device_id":    "doorbell_1",
        "device_name":  "Front Doorbell",
        "device_model": "T8200",
        "serial_number": "SN987654321",
        "battery_level": 72,
        "wifi_signal":   -50,
        "is_online":     True,
        "state":         "idle",
        "stream_url":    "rtsp://192.168.1.101:554/stream1",
        "last_event":    None,
        "type":          "doorbell",
        "properties": {
            "night_vision":     True,
            "two_way_audio":    True,
            "ringing":          False,
            "motion_detection": True,
            "motion_detected":  False,
        },
    },
    "ground_base_1": {
        "device_id":    "ground_base_1",
        "device_name":  "HomeBase",
        "device_model": "T8000",
        "serial_number": "SN456789123",
        "is_online":     True,
        "state":         "disarmed",
        "last_event":    None,
        "type":          "ground_base",
        "properties": {
            "armed":            False,
            "mode":             "disarmed",
            "schedule_enabled": False,
        },
    },
    "lock_1": {
        "device_id":    "lock_1",
        "device_name":  "Front Door Lock",
        "device_model": "T8500",
        "serial_number": "SN555555555",
        "battery_level": 90,
        "wifi_signal":   -60,
        "is_online":     True,
        "state":         "locked",
        "type":          "smart_lock",
        "properties": {
            "locked":    True,
            "locking":   False,
            "unlocking": False,
            "jammed":    False,
        },
    },
}


# -----------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------

@pytest.fixture
def eufy_username() -> str:
    """Return the Eufy account email from env, or a mock default.

    Returns:
        The value of EUFY_USERNAME env var, or "test_user" if not set.
    """
    return EUFY_USERNAME or "test_user"


@pytest.fixture
def eufy_password() -> str:
    """Return the Eufy account password from env, or a mock default.

    Returns:
        The value of EUFY_PASSWORD env var, or "test_password" if not set.
    """
    return EUFY_PASSWORD or "test_password"


@pytest.fixture
def eufy_country() -> str:
    """Return the Eufy account country code from env, or a mock default.

    Returns:
        The value of EUFY_COUNTRY env var, or "US" if not set.
    """
    return EUFY_COUNTRY or "US"


@pytest.fixture
def mock_device_data() -> dict[str, Any]:
    """Return the standard mock device data dict.

    Contains 4 simulated devices: camera_1, doorbell_1, ground_base_1,
    lock_1. Each has realistic properties matching the expected schema.

    Returns:
        A copy of MOCK_DEVICE_DATA.
    """
    return dict(MOCK_DEVICE_DATA)


@pytest.fixture
def mock_coordinator(mock_device_data: dict[str, Any]) -> MagicMock:
    """Create a mock coordinator pre-loaded with test device data.

    The mock supports:
      - coordinator.data:             The device data dict.
      - coordinator.async_set_updated_data(): AsyncMock for update tracking.
      - coordinator.async_config_entry_first_refresh(): AsyncMock.

    Use this fixture in unit tests to avoid needing a real API connection.

    Returns:
        A configured MagicMock.
    """
    coordinator = MagicMock()
    coordinator.data = mock_device_data
    coordinator.async_set_updated_data = AsyncMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.set_mode = AsyncMock(return_value=True)
    coordinator.trigger_alarm = AsyncMock(return_value=True)
    coordinator.disarm_alarm = AsyncMock(return_value=True)
    return coordinator


@pytest.fixture
def mock_config_entry() -> MagicMock:
    """Create a mock HA ConfigEntry with test credentials.

    Contains realistic username/password values for a Eufy cloud
    account. No host or port needed — Eufy uses cloud authentication.

    Returns:
        A configured MagicMock.
    """
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "username": "test_user",
        "password": "test_password",
        "country": "US",
    }
    entry.options = {}
    return entry


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock HomeAssistant instance.

    Initialises hass.data with the integration's domain key.
    Use this fixture in unit tests that need a HA instance reference.

    Returns:
        A configured MagicMock.
    """
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {DOMAIN: {}}
    hass.config = MagicMock()
    hass.config_entries = MagicMock()
    return hass


# -----------------------------------------------------------------------
# REAL DEVICE FIXTURES (require --run-real flag)
# -----------------------------------------------------------------------

@pytest.fixture
def real_coordinator(
    mock_hass: MagicMock, mock_config_entry: MagicMock
) -> Any:
    """Create a real EufyDataUpdateCoordinator connected to Eufy cloud.

    Requires EUFY_USERNAME / EUFY_PASSWORD env vars and
    --run-real CLI flag. Falls back to mock_coordinator otherwise.

    Usage:
        @pytest.mark.real_device
        def test_with_real_account(real_coordinator):
            data = await real_coordinator._fetch_devices()
            assert len(data) > 0

    Returns:
        An initialised EufyDataUpdateCoordinator.
    """
    if not HAVE_REAL_CREDENTIALS:
        pytest.skip("Real credentials not set")
    from custom_components.eufy_custom_integration.coordinator import (
        EufyDataUpdateCoordinator,
    )
    return EufyDataUpdateCoordinator(mock_hass, mock_config_entry)
