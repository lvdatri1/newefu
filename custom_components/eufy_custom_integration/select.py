"""Select platform for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    MODE_AWAY,
    MODE_CUSTOM,
    MODE_DISARMED,
    MODE_HOME,
    MODE_SCHEDULE,
)
from .coordinator import EufyDataUpdateCoordinator
from .devices.base_device import EufyDeviceEntity

AVAILABLE_MODES = [MODE_HOME, MODE_AWAY, MODE_SCHEDULE, MODE_CUSTOM, MODE_DISARMED]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy select entities."""
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyModeSelect] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") == "ground_base":
                entities.append(
                    EufyModeSelect(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufyModeSelect(EufyDeviceEntity, SelectEntity):
    """Representation of a Eufy security mode selector."""

    _attr_options = AVAILABLE_MODES

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the mode selector."""
        super().__init__(coordinator, device_id, device_info, "Security Mode")

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        return self._get_property("mode", MODE_DISARMED)

    async def async_select_option(self, option: str) -> None:
        """Change the security mode."""
        data = self._get_device_data()
        if data and option in AVAILABLE_MODES:
            properties = data.get("properties", {})
            properties["mode"] = option
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
