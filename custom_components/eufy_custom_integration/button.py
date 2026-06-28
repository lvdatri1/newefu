"""
Button platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides pressable button entities for Eufy devices. Currently:
   - **WakeUpButton**:  Wakes up a device from sleep/standby.

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyWakeUpButton per camera/doorbell/button device
   -> async_add_entities() registers it with HA
   -> async_press() -> sets device state to "waking"
"""

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
    """Set up Eufy button entities from a config entry.

    Creates a wake-up button for cameras, doorbells, and generic
    button-type devices.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
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
    """Base class for all Eufy buttons.

    Extends EufyDeviceEntity with ButtonEntity for HA button compatibility.
    Subclasses must override async_press().
    """


class EufyWakeUpButton(EufyButton):
    """Button to wake up a Eufy device from standby/sleep mode.

    Pressing this button sends a wake command to the device,
    updating its state to "waking".
    """

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the wake-up button.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Wake Up")

    async def async_press(self) -> None:
        """Press the wake-up button.

        Sends a wake command to the device and updates the state
        to "waking". The coordinator notifies HA of the change.
        """
        data = self._get_device_data()
        if data:
            data["state"] = "waking"
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
