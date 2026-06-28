"""
Alarm control panel platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides an Alarm Control Panel entity for Eufy ground bases (HomeBase).
 Supports:
   - Arm Home, Arm Away, Arm Night, Arm Custom Bypass
   - Disarm
   - Trigger
   - State display (disarmed, armed_home, armed_away, triggered, etc.)

================================================================================
 STATE MAPPING
================================================================================

 Eufy mode          -> HA alarm state
 -------------------------------------------------
 disarmed           -> STATE_ALARM_DISARMED
 home               -> STATE_ALARM_ARMED_HOME
 away               -> STATE_ALARM_ARMED_AWAY
 schedule           -> STATE_ALARM_ARMED_AWAY
 custom             -> STATE_ALARM_ARMED_CUSTOM_BYPASS
 alarm_triggered    -> STATE_ALARM_TRIGGERED

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> creates EufyAlarmControlPanel per ground_base device
   -> async_add_entities() registers it with HA
   -> state property         <- reads from device state + mode
   -> async_alarm_disarm()   -> coordinator.disarm_alarm()
   -> async_alarm_arm_*()    -> coordinator.set_mode()
   -> async_alarm_trigger()  -> coordinator.trigger_alarm()
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)
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
    """Set up Eufy alarm control panel entities from a config entry.

    Creates an alarm control panel for every ground base device.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyAlarmControlPanel] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") == "ground_base":
                entities.append(
                    EufyAlarmControlPanel(coordinator, device_id, device_info)
                )

    async_add_entities(entities)


# Mapping from Eufy internal modes to HA alarm states.
# Used by the state property to translate device state into a
# standard HA alarm state string that the frontend understands.
MODE_HA_MAP = {
    "disarmed":        STATE_ALARM_DISARMED,
    "home":            STATE_ALARM_ARMED_HOME,
    "away":            STATE_ALARM_ARMED_AWAY,
    "schedule":        STATE_ALARM_ARMED_AWAY,
    "custom":          STATE_ALARM_ARMED_CUSTOM_BYPASS,
    "alarm_triggered": STATE_ALARM_TRIGGERED,
}


class EufyAlarmControlPanel(EufyDeviceEntity, AlarmControlPanelEntity):
    """Representation of a Eufy ground base alarm control panel.

    Integrates with HA's alarm panel UI, providing arm/disarm/trigger
    controls and real-time state display.

    Usage:
        Accessible as a standard HA alarm control panel entity. Commands
        are delegated to the coordinator which communicates with the
        Eufy API.
    """

    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
        | AlarmControlPanelEntityFeature.ARM_CUSTOM_BYPASS
        | AlarmControlPanelEntityFeature.TRIGGER
    )
    _attr_code_arm_required = False

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the alarm control panel.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        super().__init__(coordinator, device_id, device_info, "Alarm")

    @property
    def state(self) -> str | None:
        """Return the current HA alarm state.

        Reads the Eufy device mode/state and maps it to a HA alarm
        state constant. Falls back to STATE_ALARM_DISARMED if the
        mode is unknown.

        The "state" field tracks transient conditions (alarm_triggered).
        The "mode" field (properties.mode) tracks the persistent security
        mode (home/away/disarmed/etc). If state is not triggered, the
        mode determines the alarm state.

        Returns:
            One of STATE_ALARM_DISARMED, STATE_ALARM_ARMED_HOME,
            STATE_ALARM_ARMED_AWAY, STATE_ALARM_ARMED_CUSTOM_BYPASS,
            STATE_ALARM_TRIGGERED, or None if no data.
        """
        data = self._get_device_data()
        if data:
            raw_state = data.get("state", "disarmed")
            if raw_state == "alarm_triggered":
                return STATE_ALARM_TRIGGERED
            mode = data.get("properties", {}).get("mode", "disarmed")
            return MODE_HA_MAP.get(mode, STATE_ALARM_DISARMED)
        return None

    # ------------------------------------------------------------------
    # COMMANDS
    # Each delegates to the coordinator which sends the command to the
    # Eufy API and updates local state.
    # ------------------------------------------------------------------

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm the alarm system.

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.disarm_alarm(self._device_id)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm the system in Home mode (partial sensors active).

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.set_mode(self._device_id, "home")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arm the system in Away mode (all sensors active).

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.set_mode(self._device_id, "away")

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Arm the system in Night mode.

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.set_mode(self._device_id, "schedule")

    async def async_alarm_arm_custom_bypass(
        self, code: str | None = None
    ) -> None:
        """Arm the system with custom bypass (custom rules).

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.set_mode(self._device_id, "custom")

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Trigger the alarm manually.

        Args:
            code: Optional security code (not currently used).
        """
        await self.coordinator.trigger_alarm(self._device_id)
