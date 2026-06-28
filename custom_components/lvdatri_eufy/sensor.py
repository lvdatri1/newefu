"""
Sensor platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides numeric sensor entities for Eufy devices:
   - **BatterySensor**:     Battery level (0-100%).
   - **WiFiSignalSensor**:  WiFi signal strength (dBm).

 One of each is created per device that has battery_level/wifi_signal data.

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyBatterySensor + EufyWiFiSignalSensor per device
   -> async_add_entities() registers them with HA
   -> each sensor reads native_value from coordinator.data[device_id]

================================================================================
 EXTENSION POINTS
================================================================================

 To add a new numeric sensor:
   1. Create a subclass of EufySensor.
   2. Override _attr_device_class and _attr_native_unit_of_measurement.
   3. Override native_value to read from _get_device_data().
   4. Instantiate it in async_setup_entry().

 Example:
     class EufyTemperatureSensor(EufySensor):
         _attr_device_class = SensorDeviceClass.TEMPERATURE
         _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

         @property
         def native_value(self):
             return self._get_property("temperature")
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
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
    """Set up Eufy sensor entities from a config entry.

    Creates battery and WiFi signal sensors for every camera, doorbell,
    ground base, and generic sensor-type device.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufySensor] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") in (
                "camera",
                "doorbell",
                "ground_base",
                "sensor",
            ):
                entities.append(
                    EufyBatterySensor(coordinator, device_id, device_info)
                )
                entities.append(
                    EufyWiFiSignalSensor(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


class EufySensor(EufyDeviceEntity, SensorEntity):
    """Base class for all numeric Eufy sensors.

    Extends EufyDeviceEntity with SensorEntity for HA sensor compatibility.
    Subclasses must override native_value.
    """


class EufyBatterySensor(EufySensor):
    """Battery level sensor for a Eufy device.

    Displays the remaining battery charge as a percentage.
    Reads from coordinator.data[device_id].battery_level.
    """

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the battery sensor.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Battery Level")

    @property
    def native_value(self) -> int | None:
        """Return the current battery level percentage.

        Returns:
            Integer 0-100, or None if unknown.
        """
        data = self._get_device_data()
        if data:
            return data.get("battery_level")
        return None


class EufyWiFiSignalSensor(EufySensor):
    """WiFi signal strength sensor for a Eufy device.

    Displays the RSSI in dBm (e.g. -45 dBm = excellent signal).
    Reads from coordinator.data[device_id].wifi_signal.
    """

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the WiFi signal sensor.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "WiFi Signal")

    @property
    def native_value(self) -> int | None:
        """Return the current WiFi signal strength in dBm.

        Returns:
            Negative integer (e.g. -45), or None if unknown.
        """
        data = self._get_device_data()
        if data:
            return data.get("wifi_signal")
        return None
