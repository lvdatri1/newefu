"""
Lock platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides a Lock entity for Eufy smart locks. Supports:
   - Lock / Unlock commands
   - State tracking (locked, unlocking, locking, jammed)

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyLock per smart_lock device
   -> async_add_entities() registers it with HA
   -> is_locked        <- properties.locked
   -> is_locking       <- properties.locking
   -> is_unlocking     <- properties.unlocking
   -> is_jammed        <- properties.jammed
   -> async_lock()     -> sets locked=True, locking=True
   -> async_unlock()   -> sets locked=False, unlocking=True
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
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
    """Set up Eufy lock entities from a config entry.

    Creates a lock entity for every smart_lock type device.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyLock] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") == "smart_lock":
                entities.append(EufyLock(coordinator, device_id, device_info))

    async_add_entities(entities)


class EufyLock(EufyDeviceEntity, LockEntity):
    """Representation of a Eufy smart lock.

    Provides lock/unlock control and state monitoring.
    Supports status tracking for locking, unlocking, and jammed states.

    Usage:
        Accessible as a standard HA lock entity. State is read
        from coordinator data and commands are sent via the coordinator.
    """

    _attr_supported_features = LockEntityFeature(0)

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the lock.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info)

    # ------------------------------------------------------------------
    # STATE PROPERTIES
    # ------------------------------------------------------------------

    @property
    def is_locked(self) -> bool | None:
        """Return True if the lock is currently locked.

        Returns:
            True if locked, False if unlocked, None if unknown.
        """
        return self._get_property("locked", False)

    @property
    def is_locking(self) -> bool:
        """Return True if the lock is in the process of locking."""
        return self._get_property("locking", False)

    @property
    def is_unlocking(self) -> bool:
        """Return True if the lock is in the process of unlocking."""
        return self._get_property("unlocking", False)

    @property
    def is_jammed(self) -> bool:
        """Return True if the lock mechanism is jammed."""
        return self._get_property("jammed", False)

    # ------------------------------------------------------------------
    # COMMANDS
    # ------------------------------------------------------------------

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the door.

        Sets the locked and locking flags, then notifies HA via the
        coordinator. The actual API call would go here (currently local).
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["locked"] = True
            properties["locking"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the door.

        Sets the unlocked and unlocking flags, then notifies HA via the
        coordinator. The actual API call would go here (currently local).
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["locked"] = False
            properties["unlocking"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
