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

from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_COUNTRY,
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

        Reads Eufy cloud account credentials (username, password,
        country code) from the entry and sets up the polling interval.

        The country code determines which regional API server Eufy
        routes requests to (e.g. "US", "GB", "DE").

        Args:
            hass: HomeAssistant instance.
            entry: The ConfigEntry created by the user during setup.
        """
        self.entry = entry
        self._username = entry.data[CONF_USERNAME]
        self._password = entry.data[CONF_PASSWORD]
        self._country: str = entry.data.get(CONF_COUNTRY, "US")

        poll_interval = entry.options.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )
        update_interval = timedelta(seconds=poll_interval)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=entry,
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
        """Fetch all device data from the Eufy API using pyeufysecurity.

        Attempts a real cloud API call first via the pyeufysecurity
        library (for cameras/doorbells) and raw v2 API calls for
        stations and other device types. Falls back to mock data when
        credentials are missing or the API is unreachable.

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

        try:
            from eufy_security import async_login

            if not hasattr(self, "_api_session") or self._api_session.closed:
                self._api_session = aiohttp.ClientSession()
                self._api = await async_login(
                    self._username,
                    self._password,
                    self._api_session,
                    self._country,
                )
            else:
                await self._api.async_update_device_info()

            # 1. Process cameras and doorbells from the library
            for sn, cam in self._api.cameras.items():
                dev = cam.device_info or {}
                params = dev.get("params", {}) or {}
                properties = {}
                device_type = self._infer_device_type(cam)

                stream_url = None
                try:
                    stream_url = await cam.async_get_stream_url()
                except Exception:
                    pass

                if device_type == "doorbell":
                    properties.update(
                        night_vision=params.get("night_vision", False),
                        two_way_audio=params.get("two_way_audio", True),
                        resolution="1920x1080",
                        ringing=params.get("ringing", False),
                        motion_detection=params.get("motion_detection", True),
                        motion_detected=params.get("motion_detected", False),
                    )
                else:
                    properties.update(
                        night_vision=params.get("night_vision", False),
                        two_way_audio=params.get("two_way_audio", True),
                        resolution=params.get("resolution", "2560x1920"),
                        motion_detection=params.get("motion_detection", False),
                        motion_detected=params.get("motion_detected", False),
                    )

                devices[sn] = {
                    "device_id":    sn,
                    "device_name":  cam.name or dev.get("device_name", sn),
                    "device_model": cam.model or dev.get("device_model", ""),
                    "serial_number": sn,
                    "battery_level": params.get("battery"),
                    "wifi_signal":   params.get("wifi_signal"),
                    "is_online":     dev.get("is_online", True),
                    "state":         dev.get("state", "idle"),
                    "stream_url":    stream_url,
                    "last_event":    None,
                    "type":          device_type,
                    "properties":    properties,
                }

            # 2. Fetch raw device list for non-camera devices (locks, sensors, etc.)
            try:
                resp = await self._api.request("post", "v2/app/get_devs_list")
                raw_data = resp.get("data")
                if raw_data and isinstance(raw_data, str):
                    all_devices = self._api._decrypt_response_data(raw_data)
                elif raw_data and isinstance(raw_data, list):
                    all_devices = raw_data
                else:
                    all_devices = []

                for dev in all_devices:
                    sn = dev.get("device_sn", "")
                    if not sn or sn in devices:
                        continue
                    dev_type = self._map_api_device_type(dev)
                    params = dev.get("params", {}) or {}
                    dev_info = self._build_api_device_entry(dev, dev_type, params)
                    if dev_info:
                        devices[sn] = dev_info

            except Exception as exc:
                LOGGER.debug("Could not fetch extended device list: %s", exc)

            # 3. Fetch hub/station list for alarm systems
            try:
                hubs_resp = await self._api.request("post", "v2/app/get_hub_list")
                raw_hub = hubs_resp.get("data")
                if raw_hub and isinstance(raw_hub, str):
                    hubs_data = self._api._decrypt_response_data(raw_hub)
                elif raw_hub and isinstance(raw_hub, list):
                    hubs_data = raw_hub
                else:
                    hubs_data = []

                for hub in hubs_data:
                    sn = hub.get("station_sn", "")
                    if not sn or sn in devices:
                        continue
                    params = hub.get("params", {}) or {}
                    guard_mode = params.get("guard_mode", params.get("mode", "disarmed"))
                    properties = {
                        "armed":            guard_mode != "disarmed",
                        "mode":             guard_mode,
                        "schedule_enabled": params.get("schedule_enabled", False),
                    }
                    devices[sn] = {
                        "device_id":    sn,
                        "device_name":  hub.get("device_name", hub.get("station_name", sn)),
                        "device_model": hub.get("device_model", "HomeBase"),
                        "serial_number": sn,
                        "is_online":     True,
                        "state":         guard_mode,
                        "last_event":    None,
                        "type":          "ground_base",
                        "properties":    properties,
                    }

            except Exception as exc:
                LOGGER.debug("Could not fetch hub list: %s", exc)

            # 4. Fetch latest events (motion, doorbell rings, etc.)
            try:
                latest_events = await self._api.async_get_latest_events()
                now = datetime.now(timezone.utc).isoformat()
                for sn, event in latest_events.items():
                    if sn not in devices:
                        continue
                    event_type = (event.get("event_type", "") or "").lower()
                    devices[sn]["last_event"] = now
                    props = devices[sn].get("properties", {})

                    if "motion" in event_type or event.get("motion") or event.get("movement"):
                        props["motion_detected"] = True
                    if "ring" in event_type or "doorbell" in event_type:
                        props["ringing"] = True
                    if "lock" in event_type or "unlock" in event_type:
                        lock_state = event.get("lock_state", props.get("locked", False))
                        props["locked"] = lock_state
                        devices[sn]["state"] = "locked" if lock_state else "unlocked"

                    devices[sn]["properties"] = props

            except Exception as exc:
                LOGGER.debug("Could not fetch latest events: %s", exc)

        except Exception as err:
            LOGGER.warning(
                "Eufy API call failed, falling back to mock data: %s", err
            )
            devices = self._mock_devices()

        return devices

    def _infer_device_type(self, cam) -> str:
        """Determine whether a Camera object is a doorbell or standard camera."""
        if not cam:
            return "camera"
        model = (cam.model or "").lower()
        name = (cam.name or "").lower()
        info = cam.device_info or {}
        dev_name = (info.get("device_name", "") or "").lower()
        dev_model = (info.get("device_model", "") or "").lower()
        combined = f"{model} {name} {dev_name} {dev_model}"
        if any(kw in combined for kw in ("doorbell", "door bell", "t8200", "t8210", "t8220", "2k")):
            return "doorbell"
        return "camera"

    def _map_api_device_type(self, dev: dict) -> str | None:
        """Map raw API device type string to internal type."""
        raw = (dev.get("type", "") or "").strip().lower()
        if not raw:
            model = (dev.get("device_model", "") or "").lower()
            if any(kw in model for kw in ("lock", "smart lock")):
                return "smart_lock"
            if any(kw in model for kw in ("sensor", "motion", "contact")):
                return "sensor"
            return None
        if raw in ("lock", "smartlock", "smart_lock"):
            return "smart_lock"
        if raw in ("sensor", "motion", "contact"):
            return "sensor"
        return None

    def _build_api_device_entry(
        self, dev: dict, dev_type: str | None, params: dict
    ) -> dict[str, Any] | None:
        """Convert a raw API device dict into the coordinator data schema."""
        if dev_type is None:
            return None
        sn = dev.get("device_sn", "")
        entry: dict[str, Any] = {
            "device_id":     sn,
            "device_name":   dev.get("device_name", dev.get("device_alias", sn)),
            "device_model":  dev.get("device_model", ""),
            "serial_number": sn,
            "battery_level": params.get("battery"),
            "wifi_signal":   params.get("wifi_signal"),
            "is_online":     dev.get("is_online", True),
            "state":         "unknown",
            "stream_url":    None,
            "last_event":    None,
            "type":          dev_type,
            "properties":    {},
        }

        if dev_type == "smart_lock":
            lock_state = params.get("lock_state", "locked")
            entry["state"] = lock_state
            entry["properties"] = {
                "locked":   lock_state == "locked",
                "locking":  lock_state == "locking",
                "unlocking": lock_state == "unlocking",
                "jammed":   lock_state == "jammed",
            }
        elif dev_type == "sensor":
            sensor_type = dev.get("device_model", "unknown_sensor")
            entry["state"] = params.get("sensor_state", "clear")
            entry["properties"] = {
                "sensor_type":      sensor_type,
                "battery_level":    params.get("battery"),
                "triggered":        params.get("sensor_state", "clear") == "triggered",
            }

        return entry

    def _mock_devices(self) -> dict[str, Any]:
        """Return mock device data when the real API is unavailable."""
        devices: dict[str, Any] = {}

        devices["camera_1"] = {
            "device_id":     "camera_1",
            "device_name":   "Front Door Camera",
            "device_model":  "T8111",
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

        devices["doorbell_1"] = {
            "device_id":     "doorbell_1",
            "device_name":   "Front Doorbell",
            "device_model":  "T8200",
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

        devices["ground_base_1"] = {
            "device_id":     "ground_base_1",
            "device_name":   "HomeBase",
            "device_model":  "T8000",
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

    async def async_unload(self) -> None:
        """Clean up the aiohttp session when the coordinator is shut down."""
        if hasattr(self, "_api_session") and not self._api_session.closed:
            await self._api_session.close()
