"""
Tests for the Eufy Alarm Control Panel platform (alarm_control_panel.py).

================================================================================
 COVERAGE
================================================================================

 - Alarm control panel initialisation (name, unique_id)
 - Supported features (arm_home, arm_away, arm_night, arm_custom, trigger)
 - State mapping: disarmed -> STATE_ALARM_DISARMED
 - State mapping: home mode -> STATE_ALARM_ARMED_HOME
 - State mapping: away mode -> STATE_ALARM_ARMED_AWAY
 - State mapping: alarm_triggered -> STATE_ALARM_TRIGGERED
 - Disarm command delegates to coordinator.disarm_alarm()
 - Arm home command delegates to coordinator.set_mode("home")
 - Arm away command delegates to coordinator.set_mode("away")
 - Arm night command delegates to coordinator.set_mode("schedule")
 - Trigger command delegates to coordinator.trigger_alarm()
"""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntityFeature,
)
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_CUSTOM_BYPASS,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)

from custom_components.eufy_custom_integration.alarm_control_panel import (
    EufyAlarmControlPanel,
)


async def test_alarm_initialization(mock_coordinator: MagicMock) -> None:
    """Verify alarm panel entity is created with correct metadata."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.name == "HomeBase Alarm"
    assert alarm.unique_id == "SN456789123_Alarm"


async def test_alarm_supported_features(mock_coordinator: MagicMock) -> None:
    """Verify alarm panel supports arm/disarm/trigger features."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    expected = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
        | AlarmControlPanelEntityFeature.ARM_CUSTOM_BYPASS
        | AlarmControlPanelEntityFeature.TRIGGER
    )
    assert alarm.supported_features == expected


async def test_alarm_disarmed_state(mock_coordinator: MagicMock) -> None:
    """Verify state is STATE_ALARM_DISARMED when mode is 'disarmed'."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_DISARMED


async def test_alarm_armed_home_state(mock_coordinator: MagicMock) -> None:
    """Verify state is STATE_ALARM_ARMED_HOME when mode is 'home'."""
    mock_coordinator.data["ground_base_1"]["properties"]["mode"] = "home"
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_ARMED_HOME


async def test_alarm_armed_away_state(mock_coordinator: MagicMock) -> None:
    """Verify state is STATE_ALARM_ARMED_AWAY when mode is 'away'."""
    mock_coordinator.data["ground_base_1"]["properties"]["mode"] = "away"
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_ARMED_AWAY


async def test_alarm_triggered_state(mock_coordinator: MagicMock) -> None:
    """Verify state is STATE_ALARM_TRIGGERED when state is 'alarm_triggered'."""
    mock_coordinator.data["ground_base_1"]["state"] = "alarm_triggered"
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_TRIGGERED


async def test_alarm_disarm(mock_coordinator: MagicMock) -> None:
    """Verify async_alarm_disarm calls coordinator.disarm_alarm()."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_disarm()
    mock_coordinator.disarm_alarm.assert_called_once_with("ground_base_1")


async def test_alarm_arm_home(mock_coordinator: MagicMock) -> None:
    """Verify async_alarm_arm_home calls coordinator.set_mode('home')."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_home()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "home")


async def test_alarm_arm_away(mock_coordinator: MagicMock) -> None:
    """Verify async_alarm_arm_away calls coordinator.set_mode('away')."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_away()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "away")


async def test_alarm_arm_night(mock_coordinator: MagicMock) -> None:
    """Verify async_alarm_arm_night calls coordinator.set_mode('schedule')."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_night()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "schedule")


async def test_alarm_trigger(mock_coordinator: MagicMock) -> None:
    """Verify async_alarm_trigger calls coordinator.trigger_alarm()."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_trigger()
    mock_coordinator.trigger_alarm.assert_called_once_with("ground_base_1")
