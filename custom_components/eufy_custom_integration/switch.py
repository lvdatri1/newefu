"""Switch platform for the Eufy Custom Integration."""

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
    """Set up Eufy switch entities."""
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
    """Base class for Eufy switches."""


class EufyMotionDetectionSwitch(EufySwitch):
    """Representation of a Eufy motion detection switch."""

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the motion detection switch."""
        super().__init__(coordinator, device_id, device_info, "Motion Detection")

    @property
    def is_on(self) -> bool:
        """Return whether motion detection is on."""
        return self._get_property("motion_detection", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on motion detection."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off motion detection."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = False
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
