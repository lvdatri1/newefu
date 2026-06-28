"""Base device class for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import EufyDataUpdateCoordinator


class EufyDeviceEntity(CoordinatorEntity[EufyDataUpdateCoordinator]):
    """Base class for Eufy device entities."""

    _attr_has_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
        entity_type: str | None = None,
    ) -> None:
        """Initialize the Eufy device entity."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_info = device_info
        self._entity_type = entity_type

        name = device_info.get("device_name", device_id)
        serial = device_info.get("serial_number", device_id)
        model = device_info.get("device_model", "Unknown")

        if entity_type:
            self._attr_name = f"{name} {entity_type}"
            self._attr_unique_id = f"{serial}_{entity_type}"
        else:
            self._attr_name = name
            self._attr_unique_id = serial

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=name,
            manufacturer=MANUFACTURER,
            model=model,
            serial_number=serial,
            sw_version=device_info.get("firmware_version"),
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and bool(self.coordinator.data)
            and self._device_id in self.coordinator.data
        )

    def _get_device_data(self) -> dict[str, Any] | None:
        """Get the device data from coordinator."""
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id]
        return None

    def _get_property(self, key: str, default: Any = None) -> Any:
        """Get a property from device data."""
        data = self._get_device_data()
        if data:
            return data.get("properties", {}).get(key, default)
        return default
