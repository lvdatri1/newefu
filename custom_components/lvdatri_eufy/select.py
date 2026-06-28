"""
Select platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides a dropdown selector entity for the ground base security mode.
 Users can switch between: home, away, schedule, custom, disarmed.

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyModeSelect per ground_base device
   -> async_add_entities() registers it with HA
   -> current_option     <- properties.mode
   -> async_select_option -> calls coordinator.set_mode()
"""

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

# The full set of security modes available in the selector dropdown.
AVAILABLE_MODES = [MODE_HOME, MODE_AWAY, MODE_SCHEDULE, MODE_CUSTOM, MODE_DISARMED]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy select entities from a config entry.

    Creates a security mode selector for every ground base device.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
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
    """Dropdown selector for a ground base's security mode.

    Allows the user to choose the operating mode:
      - home:      Armed while at home (partial sensors active)
      - away:      Fully armed
      - schedule:  Follows a preset schedule
      - custom:    Custom rules
      - disarmed:  All sensors inactive

    State is stored in coordinator.data[device_id].properties.mode.
    """

    _attr_options = AVAILABLE_MODES

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the mode selector.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Security Mode")

    @property
    def current_option(self) -> str | None:
        """Return the currently selected security mode.

        Returns:
            One of "home", "away", "schedule", "custom", "disarmed",
            or None if not yet set.
        """
        return self._get_property("mode", MODE_DISARMED)

    async def async_select_option(self, option: str) -> None:
        """Change the security mode to a new value.

        Delegates the actual command to the coordinator, which
        communicates with the Eufy API.

        Args:
            option: One of the AVAILABLE_MODES strings.
        """
        data = self._get_device_data()
        if data and option in AVAILABLE_MODES:
            properties = data.get("properties", {})
            properties["mode"] = option
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
