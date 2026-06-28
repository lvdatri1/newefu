"""Alarm control panel platform for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
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
    """Set up Eufy alarm control panel entities."""
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


MODE_HA_MAP = {
    "disarmed": STATE_ALARM_DISARMED,
    "home": STATE_ALARM_ARMED_HOME,
    "away": STATE_ALARM_ARMED_AWAY,
    "schedule": STATE_ALARM_ARMED_AWAY,
    "custom": STATE_ALARM_ARMED_CUSTOM_BYPASS,
    "alarm_triggered": STATE_ALARM_TRIGGERED,
}


class EufyAlarmControlPanel(EufyDeviceEntity, AlarmControlPanelEntity):
    """Representation of a Eufy alarm control panel."""

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
        """Initialize the alarm control panel."""
        super().__init__(coordinator, device_id, device_info, "Alarm")

    @property
    def state(self) -> str | None:
        """Return the state of the alarm."""
        data = self._get_device_data()
        if data:
            raw_state = data.get("state", "disarmed")
            if raw_state in MODE_HA_MAP:
                return MODE_HA_MAP[raw_state]
            mode = data.get("properties", {}).get("mode", "disarmed")
            return MODE_HA_MAP.get(mode, STATE_ALARM_DISARMED)
        return None

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self.coordinator.disarm_alarm(self._device_id)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self.coordinator.set_mode(self._device_id, "home")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self.coordinator.set_mode(self._device_id, "away")

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        await self.coordinator.set_mode(self._device_id, "schedule")

    async def async_alarm_arm_custom_bypass(
        self, code: str | None = None
    ) -> None:
        """Send arm custom bypass command."""
        await self.coordinator.set_mode(self._device_id, "custom")

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        await self.coordinator.trigger_alarm(self._device_id)
