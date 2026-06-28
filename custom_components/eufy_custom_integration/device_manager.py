"""
Device manager for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 The device manager bridges between the coordinator's flat device data and
 Home Assistant's device registry. It:
   - Registers each Eufy device as a HA device entry (with model, serial, etc.)
   - Provides lookup methods for entities to find their parent device.
   - Handles device updates when the coordinator refreshes data.

================================================================================
 DEVICE REGISTRY INTEGRATION
================================================================================

 Each Eufy device is registered with:
   - identifiers:  {(DOMAIN, device_id)}  --  unique tuple for matching
   - name:         user-friendly name from the device
   - model:        hardware model string (e.g. "T8111")
   - manufacturer: "Eufy"
   - sw_version:   firmware version (optional)
   - serial_number: hardware serial number

 Entities created for this device will automatically be linked to it via
 the device_info attribute in EufyDeviceEntity.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MANUFACTURER
from .coordinator import EufyDataUpdateCoordinator


class EufyDeviceManager:
    """Manages Eufy devices in Home Assistant's device registry.

    Each Eufy device (camera, doorbell, ground base, etc.) is registered
    as a HA device so that entities created from it are grouped together
    in the UI.

    Attributes:
        hass:        HomeAssistant instance.
        coordinator: The data coordinator for state lookups.
        devices:     Internal cache of {device_id -> {device_info, device_entry}}.

    Usage:
        manager = EufyDeviceManager(hass, coordinator)
        await manager.async_register_device("camera_1", device_info)
        device = manager.get_device("camera_1")
    """

    def __init__(
        self, hass: HomeAssistant, coordinator: EufyDataUpdateCoordinator
    ) -> None:
        """Initialise the device manager.

        Args:
            hass:        HomeAssistant instance.
            coordinator: The data coordinator (provides device info via data).
        """
        self.hass = hass
        self.coordinator = coordinator
        self.devices: dict[str, dict[str, Any]] = {}

    async def async_setup(self) -> None:
        """Set up all devices from the current coordinator data.

        Iterates over every device in coordinator.data and registers it
        in the HA device registry. Call this after the first data refresh.
        """
        data = self.coordinator.data or {}
        for device_id, device_info in data.items():
            await self.async_register_device(device_id, device_info)

    async def async_register_device(
        self, device_id: str, device_info: dict[str, Any]
    ) -> dr.DeviceEntry | None:
        """Register (or update) a device in the HA device registry.

        If the device already exists (matched by DOMAIN + device_id),
        its entry is updated in-place. Otherwise a new entry is created.

        Args:
            device_id:   The unique ID of the Eufy device.
            device_info: Dict with keys: device_name, device_model,
                         serial_number, firmware_version, etc.

        Returns:
            The HA DeviceEntry for the registered device, or None if
            registration failed.
        """
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
        """Update device information in the registry.

        Call this when coordinator data changes (e.g. firmware update).

        Args:
            device_id:   The unique ID of the Eufy device.
            device_info: Updated info dict (at minimum device_name).
        """
        device_registry = dr.async_get(self.hass)
        identifiers = {(DOMAIN, device_id)}
        device = device_registry.async_get_device(identifiers=identifiers)

        if device:
            device_registry.async_update_device(
                device.id,
                name=device_info.get("device_name"),
            )

    def get_device(self, device_id: str) -> dict[str, Any] | None:
        """Get a registered device by its device_id.

        Args:
            device_id: The unique Eufy device ID.

        Returns:
            Internal device dict (with "device_info" and "device_entry"
            keys) or None if not found.
        """
        return self.devices.get(device_id)

    def get_all_devices(self) -> dict[str, dict[str, Any]]:
        """Get all registered devices.

        Returns:
            Dict mapping device_id -> internal device dict.
        """
        return self.devices
