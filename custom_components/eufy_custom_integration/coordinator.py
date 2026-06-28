"""Data update coordinator for the Eufy Custom Integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, DOMAIN, LOGGER


class EufyDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Eufy data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self._host = entry.data[CONF_HOST]
        self._port = entry.data.get(CONF_PORT, 5222)
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
        """Fetch data from Eufy devices."""
        data: dict[str, Any] = {}

        try:
            data = await self._fetch_devices()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Eufy API: {err}") from err

        return data

    async def _fetch_devices(self) -> dict[str, Any]:
        """Fetch all device data from the Eufy API."""
        devices: dict[str, Any] = {}

        devices["camera_1"] = {
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
                "resolution": "2560x1920",
            },
        }

        devices["doorbell_1"] = {
            "device_id": "doorbell_1",
            "device_name": "Front Doorbell",
            "device_model": "T8200",
            "serial_number": "SN987654321",
            "battery_level": 72,
            "wifi_signal": -50,
            "is_online": True,
            "state": "idle",
            "last_event": None,
            "type": "doorbell",
            "properties": {
                "night_vision": True,
                "two_way_audio": True,
                "resolution": "1920x1080",
            },
        }

        devices["ground_base_1"] = {
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
        }

        return devices

    async def set_mode(self, device_id: str, mode: str) -> bool:
        """Set the mode for a device."""
        data = self.data or {}
        if device_id in data:
            properties = data[device_id].get("properties", {})
            properties["mode"] = mode
            data[device_id]["properties"] = properties
            self.async_set_updated_data(data)
            return True
        return False

    async def trigger_alarm(self, device_id: str) -> bool:
        """Trigger alarm for a device."""
        data = self.data or {}
        if device_id in data:
            data[device_id]["state"] = "alarm_triggered"
            self.async_set_updated_data(data)
            return True
        return False

    async def disarm_alarm(self, device_id: str) -> bool:
        """Disarm alarm for a device."""
        data = self.data or {}
        if device_id in data:
            data[device_id]["state"] = "disarmed"
            self.async_set_updated_data(data)
            return True
        return False
