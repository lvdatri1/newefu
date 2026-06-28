"""
Base device entity for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 EufyDeviceEntity is the base class for ALL Eufy entities. It extends
 CoordinatorEntity so that every entity:
   - Automatically listens to coordinator updates.
   - Marks itself unavailable when the coordinator has no data.
   - Provides helper methods for accessing device data.

 Every platform entity (EufyCamera, EufySensor, EufySwitch, etc.)
 should inherit from this class.

================================================================================
 HIERARCHY
================================================================================

 CoordinatorEntity (HA base -- handles data refresh subscription)
        |
   EufyDeviceEntity (this class -- adds device_info, helpers)
        |
   +-- EufyCamera
   +-- EufySensor (-> EufyBatterySensor, EufyWiFiSignalSensor)
   +-- EufyBinarySensor (-> EufyMotionSensor, EufyOnlineSensor, ...)
   +-- EufySwitch (-> EufyMotionDetectionSwitch)
   +-- EufyButton (-> EufyWakeUpButton)
   +-- EufyLock
   +-- EufyModeSelect
   +-- EufyAlarmControlPanel

================================================================================
 EXTENSION POINTS
================================================================================

 To create a new entity type:
   1. Subclass EufyDeviceEntity.
   2. Add entity-specific properties and methods.
   3. Call the parent constructor with the right entity_type string.
   4. Add an async_setup_entry() function in the platform file.
"""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN, MANUFACTURER
from ..coordinator import EufyDataUpdateCoordinator


class EufyDeviceEntity(CoordinatorEntity[EufyDataUpdateCoordinator]):
    """Base class for all Eufy device entities.

    Provides:
      - Automatic device_info linking to the HA device registry.
      - Unique ID generation based on serial_number + entity_type.
      - Availability tracking (unavailable if coordinator has no data).
      - Helper methods _get_device_data() and _get_property().

    Attributes:
        _device_id:    The Eufy device ID (e.g. "camera_1").
        _device_info:  The raw device info dict from the coordinator.
        _entity_type:  Optional suffix for name/unique_id (e.g. "Battery").

    Usage:
        class EufyMyEntity(EufyDeviceEntity):
            def __init__(self, coordinator, device_id, device_info):
                super().__init__(coordinator, device_id, device_info, "MyFeature")
    """

    _attr_has_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
        entity_type: str | None = None,
    ) -> None:
        """Initialise the Eufy device entity.

        Sets up:
          - name/unique_id:  If entity_type is given, appends it
                             (e.g. "Front Door Camera Battery").
          - device_info:     Links this entity to the HA device registry
                             entry for the parent device.

        Args:
            coordinator: The data coordinator for state updates.
            device_id:   The Eufy device ID.
            device_info: The device data dict from the coordinator.
            entity_type: Optional type name appended to the entity's
                         display name and unique_id.
        """
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

        # Link to the device registry entry created by EufyDeviceManager.
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
        """Return True if the entity is available.

        An entity is available when:
          1. The coordinator itself is available (base class check).
          2. The coordinator has data (not None or empty).
          3. The device_id exists in the current data.

        Returns:
            True if the entity should be shown as available in HA.
        """
        return (
            super().available
            and bool(self.coordinator.data)
            and self._device_id in self.coordinator.data
        )

    def _get_device_data(self) -> dict[str, Any] | None:
        """Get the current device data from the coordinator.

        Convenience method that safely reads from coordinator.data.

        Returns:
            The device data dict if available, or None if the device
            is not in the current data snapshot.
        """
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id]
        return None

    def _get_property(self, key: str, default: Any = None) -> Any:
        """Get a typed property from the device's 'properties' dict.

        This is the primary way to access device-specific state like
        motion_detection, ringing, locked, etc.

        Args:
            key:     The property key (e.g. "motion_detection").
            default: Value to return if the key is not found.

        Returns:
            The property value, or the default if not present.
        """
        data = self._get_device_data()
        if data:
            return data.get("properties", {}).get(key, default)
        return default
