"""Lock platform for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_LOCKED, STATE_UNLOCKED
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
    """Set up Eufy lock entities."""
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
    """Representation of a Eufy smart lock."""

    _attr_supported_features = LockEntityFeature(0)

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the lock."""
        super().__init__(coordinator, device_id, device_info)

    @property
    def is_locked(self) -> bool | None:
        """Return whether the lock is locked."""
        return self._get_property("locked", False)

    @property
    def is_locking(self) -> bool:
        """Return whether the lock is locking."""
        return self._get_property("locking", False)

    @property
    def is_unlocking(self) -> bool:
        """Return whether the lock is unlocking."""
        return self._get_property("unlocking", False)

    @property
    def is_jammed(self) -> bool:
        """Return whether the lock is jammed."""
        return self._get_property("jammed", False)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the lock."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["locked"] = True
            properties["locking"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the lock."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["locked"] = False
            properties["unlocking"] = True
            data["properties"] = properties
            self.coordinator.async_set_updated_data(self.coordinator.data or {})
