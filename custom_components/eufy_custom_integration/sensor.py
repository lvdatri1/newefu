"""Sensor platform for the Eufy Custom Integration."""

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
    """Set up Eufy sensor entities."""
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
    """Base class for Eufy sensors."""


class EufyBatterySensor(EufySensor):
    """Representation of a Eufy battery sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator, device_id, device_info, "Battery Level")

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        data = self._get_device_data()
        if data:
            return data.get("battery_level")
        return None


class EufyWiFiSignalSensor(EufySensor):
    """Representation of a Eufy WiFi signal sensor."""

    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the WiFi signal sensor."""
        super().__init__(coordinator, device_id, device_info, "WiFi Signal")

    @property
    def native_value(self) -> int | None:
        """Return the WiFi signal strength."""
        data = self._get_device_data()
        if data:
            return data.get("wifi_signal")
        return None
