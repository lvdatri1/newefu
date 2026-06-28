"""
Binary sensor platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides binary (on/off) sensors for Eufy devices:
   - **MotionSensor**:       Detects motion on cameras and doorbells.
   - **OnlineSensor**:       Device connectivity status.
   - **DoorbellPressSensor**: Doorbell ringing detection.

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates binary sensors per device based on type
   -> async_add_entities() registers them with HA
   -> each sensor reads is_on from coordinator.data[device_id] properties
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up Eufy binary sensor entities from a config entry.

    Creates motion and online sensors for cameras, doorbells, and generic
    sensor devices. Also creates a doorbell press sensor for doorbells.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyBinarySensor] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            device_type = device_info.get("type")
            if device_type in ("camera", "doorbell", "sensor"):
                entities.append(
                    EufyMotionSensor(coordinator, device_id, device_info)
                )
                entities.append(
                    EufyOnlineSensor(coordinator, device_id, device_info)
                )
            if device_type == "doorbell":
                entities.append(
                    EufyDoorbellPressSensor(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufyBinarySensor(EufyDeviceEntity, BinarySensorEntity):
    """Base class for all Eufy binary sensors.

    Extends EufyDeviceEntity with BinarySensorEntity for HA binary
    sensor compatibility. Subclasses must override is_on.
    """


class EufyMotionSensor(EufyBinarySensor):
    """Motion detection sensor for a Eufy camera or doorbell.

    Turns on when motion is detected, off when clear.
    Reads from properties.motion_detected.
    """

    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the motion sensor.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Motion")

    @property
    def is_on(self) -> bool:
        """Return True if motion is currently being detected."""
        return self._get_property("motion_detected", False)


class EufyOnlineSensor(EufyBinarySensor):
    """Connectivity sensor for a Eufy device.

    Turns on when the device is reachable on the network.
    Reads from is_online in the device data.
    """

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the online sensor.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Online")

    @property
    def is_on(self) -> bool:
        """Return True if the device is currently online and reachable."""
        data = self._get_device_data()
        if data:
            return data.get("is_online", False)
        return False


class EufyDoorbellPressSensor(EufyBinarySensor):
    """Doorbell press sensor for a Eufy doorbell.

    Turns on when someone presses the doorbell button.
    Reads from properties.ringing.
    """

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the doorbell press sensor.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Ring")

    @property
    def is_on(self) -> bool:
        """Return True if the doorbell is currently ringing."""
        return self._get_property("ringing", False)
