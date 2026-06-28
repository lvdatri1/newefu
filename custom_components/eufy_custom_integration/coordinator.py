"""
Data update coordinator for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 The coordinator is the central data hub. It:
   - Polls the Eufy API at a configurable interval.
   - Holds the latest device state in self.data (a dict[str, dict]).
   - Notifies listening entities when data changes.
   - Provides command methods (set_mode, trigger_alarm, etc.) that platforms
     call to send commands back to Eufy devices.

================================================================================
 DATA STRUCTURE
================================================================================

 self.data is a dict keyed by device_id. Each value is a dict:
 {
     "device_id":   str,          # unique identifier
     "device_name": str,          # user-friendly name
     "device_model": str,         # model number (e.g. T8111)
     "serial_number": str,        # hardware serial
     "battery_level": int | None, # 0-100 percentage
     "wifi_signal":  int | None,  # dBm (e.g. -45)
     "is_online":    bool,        # connectivity status
     "state":        str,         # current operational state
     "stream_url":   str | None,  # RTSP URL for cameras/doorbells
     "last_event":   str | None,  # ISO timestamp of last event
     "type":         str,         # device type discriminator
     "properties":   dict,        # type-specific key/value store
 }

 The "properties" sub-dict is type-specific:
   camera:     { night_vision, two_way_audio, resolution, motion_detection }
   doorbell:   { night_vision, two_way_audio, resolution, ringing }
   ground_base:{ armed, mode, schedule_enabled }
   smart_lock: { locked, locking, unlocking, jammed }

================================================================================
 EXTENSION POINTS
================================================================================

 To add a new command:
   1. Implement the method here (e.g. async_set_light()).
   2. Call it from the relevant platform entity.
   3. Optionally expose as a service in services.yaml.

 To switch from mock data to a real API:
   1. Replace _fetch_devices() with a call to eufy-security-client.
   2. Keep the same return dict structure so entities continue working.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_POLL_INTERVAL,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    LOGGER,
)


class EufyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manages fetching and pushing state for all Eufy devices.

    Attributes:
        entry:      The HA ConfigEntry for this integration instance.
        data:       Dict of all device states, keyed by device_id.
                    Updated every poll_interval seconds.

    Usage:
        coordinator = EufyDataUpdateCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()
        state = coordinator.data["camera_1"]["battery_level"]
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialise the coordinator from a config entry.

        Reads Eufy cloud account credentials (username + password)
        from the entry and sets up the polling interval.

        No host or port is needed — Eufy uses cloud authentication.
        The eufy-security-client library handles the connection to
        Eufy's servers automatically.

        Args:
            hass: HomeAssistant instance.
            entry: The ConfigEntry created by the user during setup.
        """
        self.entry = entry
        self._username = entry.data[CONF_USERNAME]
        self._password = entry.data[CONF_PASSWORD]

        poll_interval = entry.options.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )
        update_interval = timedelta(seconds=poll_interval)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch fresh data from Eufy devices.

        This is called automatically by the base class on the configured
        update_interval. It wraps _fetch_devices() with error handling.

        Returns:
            Full device data dict, or an empty dict on failure.

        Raises:
            UpdateFailed: If communication with the Eufy API fails.
                          This causes HA to mark entities as unavailable.
        """
        data: dict[str, Any] = {}
        try:
            data = await self._fetch_devices()
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Eufy API: {err}"
            ) from err
        return data

    async def _fetch_devices(self) -> dict[str, Any]:
        """Fetch all device data from the Eufy API.

        CURRENTLY USES MOCK DATA. Replace this method with a real API
        call to eufy-security-client when connecting to a real Eufy hub.

        Expected return format for each device:
            device_id (str) -> {
                "device_id":   str, "device_name": str,
                "device_model": str, "serial_number": str,
                "battery_level": int|None, "wifi_signal": int|None,
                "is_online": bool, "state": str,
                "stream_url": str|None, "last_event": str|None,
                "type": str, "properties": dict,
            }

        Returns:
            Dict mapping device_id -> device info dict.
        """
        devices: dict[str, Any] = {}

        # --- Camera -------------------------------------------------------
        devices["camera_1"] = {
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
                "resolution":       "2560x1920",
                "motion_detection": False,
                "motion_detected":  False,
            },
        }

        # --- Doorbell -----------------------------------------------------
        devices["doorbell_1"] = {
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
                "resolution":       "1920x1080",
                "ringing":          False,
                "motion_detection": True,
                "motion_detected":  False,
            },
        }

        # --- Ground Base (HomeBase) ---------------------------------------
        devices["ground_base_1"] = {
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
        }

        return devices

    # ------------------------------------------------------------------
    # COMMAND METHODS
    # These are called by platform entities to send commands to devices.
    # Each method updates the local data dict and triggers a re-notify
    # so that HA entities reflect the new state immediately.
    # ------------------------------------------------------------------

    async def set_mode(self, device_id: str, mode: str) -> bool:
        """Set the security mode for a ground base device.

        Sends the mode change to the Eufy API (mock: updates local state).

        Args:
            device_id: The target device's ID.
            mode:      One of "home", "away", "schedule", "custom", "disarmed".

        Returns:
            True if the mode was updated, False if device_id is unknown.
        """
        data = self.data or {}
        if device_id not in data:
            return False
        properties = data[device_id].get("properties", {})
        properties["mode"] = mode
        data[device_id]["properties"] = properties
        self.async_set_updated_data(data)
        return True

    async def trigger_alarm(self, device_id: str) -> bool:
        """Trigger the alarm on a device.

        Args:
            device_id: The target device's ID.

        Returns:
            True if the alarm was triggered, False if device is unknown.
        """
        data = self.data or {}
        if device_id not in data:
            return False
        data[device_id]["state"] = "alarm_triggered"
        self.async_set_updated_data(data)
        return True

    async def disarm_alarm(self, device_id: str) -> bool:
        """Disarm the alarm on a device.

        Args:
            device_id: The target device's ID.

        Returns:
            True if the alarm was disarmed, False if device is unknown.
        """
        data = self.data or {}
        if device_id not in data:
            return False
        data[device_id]["state"] = "disarmed"
        self.async_set_updated_data(data)
        return True
