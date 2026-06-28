"""Button platform for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up Eufy button entities."""
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyButton] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") in ("camera", "doorbell", "button"):
                entities.append(
                    EufyWakeUpButton(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufyButton(EufyDeviceEntity, ButtonEntity):
    """Base class for Eufy buttons."""


class EufyWakeUpButton(EufyButton):
    """Representation of a Eufy wake-up button."""

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the wake-up button."""
        super().__init__(coordinator, device_id, device_info, "Wake Up")

    async def async_press(self) -> None:
        """Wake up the device."""
        data = self._get_device_data()
        if data:
            data["state"] = "waking"
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
