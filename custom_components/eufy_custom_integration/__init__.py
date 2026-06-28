"""Eufy Custom Integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import EufyDataUpdateCoordinator
from .device_manager import EufyDeviceManager

PLATFORMS: list[Platform] = [
    Platform.CAMERA,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.LOCK,
    Platform.ALARM_CONTROL_PANEL,
]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Eufy integration from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy from a config entry."""
    coordinator = EufyDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    device_manager = EufyDeviceManager(hass, coordinator)
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "device_manager": device_manager,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
