"""
Eufy Custom Integration for Home Assistant.

================================================================================
 ARCHITECTURE OVERVIEW
================================================================================

 This integration connects Home Assistant to Eufy security devices (cameras,
 doorbells, ground bases, smart locks, sensors) via the eufy-security-client
 library.

 DATA FLOW:
   Eufy Cloud/API
        |
   EufyDataUpdateCoordinator  (polling + push updates)
        |
   EufyDeviceManager          (HA device registry management)
        |
   Platform entities          (camera, sensor, binary_sensor, switch, etc.)
        |
   Home Assistant frontend

 ENTITY HIERARCHY:
   CoordinatorEntity (HA base)
        |
   EufyDeviceEntity  (base_device.py)
        |
   +-- EufyCamera
   +-- EufySensor (Battery, WiFi)
   +-- EufySwitch (Motion Detection)
   +-- EufyBinarySensor (Motion, Online, Doorbell Press)
   +-- EufyButton (Wake Up)
   +-- EufyLock
   +-- EufyModeSelect (Security Mode)
   +-- EufyAlarmControlPanel

 CONFIG ENTRY FLOW:
   async_setup_entry() in __init__.py
        |
   EufyDataUpdateCoordinator.__init__()
        |
   coordinator.async_config_entry_first_refresh()
        |
   EufyDeviceManager.__init__()
        |
   async_forward_entry_setups() for each platform

 EXTENSION POINTS:
   - Add new device types:  Create a new API client method, a new platform
     file (e.g. cover.py), and register in PLATFORMS list.
   - Add new sensors:       Add to sensor.py or binary_sensor.py following
     existing patterns (see EufyBatterySensor as a template).
   - Custom services:       Add to services.yaml and implement in
     coordinator.py or the relevant platform.
"""

from __future__ import annotations

import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import CONF_COUNTRY, DOMAIN, LOGGER
from .coordinator import EufyDataUpdateCoordinator
from .device_manager import EufyDeviceManager

# -----------------------------------------------------------------------
# PLATFORMS
# The full list of entity platforms this integration supports. Each entry
# must have a corresponding <platform>.py file with async_setup_entry().
# When adding a new platform, add it here and create the platform file.
# -----------------------------------------------------------------------
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
    """Set up the Eufy integration from YAML or environment variables.

    Called once when HA starts. If the EUFY_USERNAME, EUFY_PASSWORD,
    and EUFY_COUNTRY environment variables are all set, a config entry
    is created automatically — no UI workflow needed.

    Users can set these vars in their HA runtime environment:
      - Home Assistant OS / Supervised: add an env_vars entry in
        configuration.yaml or use the OS-level env configuration.
      - Home Assistant Container: pass -e EUFY_USERNAME=... to Docker.
      - Home Assistant Core: export in the shell before starting HA.

    Args:
        hass: HomeAssistant instance.
        config: The full HA configuration dictionary.

    Returns:
        True if setup succeeded.
    """
    hass.data.setdefault(DOMAIN, {})

    username = os.environ.get("EUFY_USERNAME")
    password = os.environ.get("EUFY_PASSWORD")
    country = os.environ.get("EUFY_COUNTRY")

    if username and password and country:
        if not hass.config_entries.async_entries(DOMAIN):
            LOGGER.info(
                "Auto-creating config entry from EUFY_USERNAME env var"
            )
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": "import"},
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_COUNTRY: country,
                    },
                )
            )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eufy from a config entry (UI-based configuration).

    This is the main entry point for the integration. It:
      1. Creates the data coordinator that polls the Eufy API.
      2. Performs an initial data refresh.
      3. Creates the device manager for HA device registry integration.
      4. Forwards setup to all registered platforms.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry created by the user during setup.

    Returns:
        True if setup succeeded.
    """
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
    """Unload a config entry.

    Called when the user removes the integration or HA shuts down.
    Tears down all platform entities and cleans up domain data.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry to unload.

    Returns:
        True if all platforms unloaded successfully.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]
    await coordinator.async_unload()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove a config entry from a device.

    Allows users to delete orphaned devices from the HA device registry.

    Args:
        hass: HomeAssistant instance.
        config_entry: The ConfigEntry.
        device_entry: The DeviceEntry to remove.

    Returns:
        True if the device can be removed.
    """
    return True
