"""
Switch platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides toggle switches for Eufy device features. Currently:
   - **MotionDetectionSwitch**:  Enables/disables motion detection on cameras
                                 and doorbells.

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyMotionDetectionSwitch per camera/doorbell/switch-type device
   -> async_add_entities() registers them with HA
   -> is_on         <- properties.motion_detection
   -> async_turn_on -> sets properties.motion_detection = True
   -> async_turn_off -> sets properties.motion_detection = False

================================================================================
 EXTENSION POINTS
================================================================================

 To add a new toggle:
   1. Subclass EufySwitch.
   2. Override is_on, async_turn_on, async_turn_off.
   3. Instantiate in async_setup_entry().
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import EufyDataUpdateCoordinator
from .devices.base_device import EufyDeviceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy switch entities from a config entry.

    Creates a motion detection switch for every camera, doorbell, and
    generic switch-type device.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufySwitch] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") in ("camera", "doorbell", "switch"):
                entities.append(
                    EufyMotionDetectionSwitch(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufySwitch(EufyDeviceEntity, SwitchEntity):
    """Base class for all Eufy switches.

    Extends EufyDeviceEntity with SwitchEntity for HA toggle compatibility.
    Subclasses must override is_on, async_turn_on, async_turn_off.
    """


class EufyMotionDetectionSwitch(EufySwitch):
    """Toggle for a Eufy device's motion detection.

    When turned on, the camera/doorbell will detect motion and fire
    events. When turned off, motion detection is disabled.

    State is stored in coordinator.data[device_id].properties.motion_detection.
    """

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the motion detection switch.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Motion Detection")

    @property
    def is_on(self) -> bool:
        """Return True if motion detection is currently enabled."""
        return self._get_property("motion_detection", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable motion detection.

        Updates the local property and triggers a coordinator re-notify
        so HA entities see the new state immediately.
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable motion detection.

        Updates the local property and triggers a coordinator re-notify.
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = False
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
