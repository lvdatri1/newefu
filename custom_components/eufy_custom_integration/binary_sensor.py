"""Binary sensor platform for the Eufy Custom Integration."""

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
    """Set up Eufy binary sensor entities."""
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyBinarySensor] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") in ("camera", "doorbell", "sensor"):
                entities.append(
                    EufyMotionSensor(coordinator, device_id, device_info)
                )
                entities.append(
                    EufyOnlineSensor(coordinator, device_id, device_info)
                )
            if device_info.get("type") == "doorbell":
                entities.append(
                    EufyDoorbellPressSensor(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufyBinarySensor(EufyDeviceEntity, BinarySensorEntity):
    """Base class for Eufy binary sensors."""


class EufyMotionSensor(EufyBinarySensor):
    """Representation of a Eufy motion sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the motion sensor."""
        super().__init__(coordinator, device_id, device_info, "Motion")

    @property
    def is_on(self) -> bool:
        """Return whether motion is detected."""
        return self._get_property("motion_detected", False)


class EufyOnlineSensor(EufyBinarySensor):
    """Representation of a Eufy online status sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the online sensor."""
        super().__init__(coordinator, device_id, device_info, "Online")

    @property
    def is_on(self) -> bool:
        """Return whether the device is online."""
        data = self._get_device_data()
        if data:
            return data.get("is_online", False)
        return False


class EufyDoorbellPressSensor(EufyBinarySensor):
    """Representation of a Eufy doorbell press sensor."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the doorbell press sensor."""
        super().__init__(coordinator, device_id, device_info, "Ring")

    @property
    def is_on(self) -> bool:
        """Return whether the doorbell is ringing."""
        return self._get_property("ringing", False)
