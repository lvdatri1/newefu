"""Device manager for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN, MANUFACTURER
from .coordinator import EufyDataUpdateCoordinator


class EufyDeviceManager:
    """Manages Eufy devices and their representation in Home Assistant."""

    def __init__(
        self, hass: HomeAssistant, coordinator: EufyDataUpdateCoordinator
    ) -> None:
        """Initialize the device manager."""
        self.hass = hass
        self.coordinator = coordinator
        self.devices: dict[str, dict[str, Any]] = {}

    async def async_setup(self) -> None:
        """Set up devices from coordinator data."""
        data = self.coordinator.data or {}
        for device_id, device_info in data.items():
            await self.async_register_device(device_id, device_info)

    async def async_register_device(
        self, device_id: str, device_info: dict[str, Any]
    ) -> dr.DeviceEntry | None:
        """Register a device in the device registry."""
        device_registry = dr.async_get(self.hass)

        device = device_registry.async_get_or_create(
            config_entry_id=self.coordinator.entry.entry_id,
            identifiers={(DOMAIN, device_id)},
            name=device_info.get("device_name", device_id),
            model=device_info.get("device_model"),
            manufacturer=MANUFACTURER,
            sw_version=device_info.get("firmware_version"),
            serial_number=device_info.get("serial_number"),
        )

        self.devices[device_id] = {
            "device_info": device_info,
            "device_entry": device,
        }

        return device

    async def async_update_device(
        self, device_id: str, device_info: dict[str, Any]
    ) -> None:
        """Update device information."""
        device_registry = dr.async_get(self.hass)
        identifiers = {(DOMAIN, device_id)}
        device = device_registry.async_get_device(identifiers=identifiers)

        if device:
            device_registry.async_update_device(
                device.id,
                name=device_info.get("device_name"),
            )

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get a device by ID."""
        return self.devices.get(device_id)

    def get_all_devices(self) -> dict[str, dict[str, Any]]:
        """Get all registered devices."""
        return self.devices
