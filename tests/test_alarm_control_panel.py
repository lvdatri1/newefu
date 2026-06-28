"""Tests for the Eufy Alarm Control Panel platform."""

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
    """Test alarm initialization."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.name == "HomeBase Alarm"
    assert alarm.unique_id == "SN456789123_Alarm"


async def test_alarm_supported_features(mock_coordinator: MagicMock) -> None:
    """Test alarm supported features."""
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
    """Test alarm disarmed state."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_DISARMED


async def test_alarm_armed_home_state(mock_coordinator: MagicMock) -> None:
    """Test alarm armed home state."""
    device_info = dict(mock_coordinator.data["ground_base_1"])
    device_info["properties"] = {"mode": "home"}
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_ARMED_HOME


async def test_alarm_armed_away_state(mock_coordinator: MagicMock) -> None:
    """Test alarm armed away state."""
    device_info = dict(mock_coordinator.data["ground_base_1"])
    device_info["properties"] = {"mode": "away"}
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_ARMED_AWAY


async def test_alarm_triggered_state(mock_coordinator: MagicMock) -> None:
    """Test alarm triggered state."""
    device_info = dict(mock_coordinator.data["ground_base_1"])
    device_info["state"] = "alarm_triggered"
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    assert alarm.state == STATE_ALARM_TRIGGERED


async def test_alarm_disarm(mock_coordinator: MagicMock) -> None:
    """Test alarm disarm."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_disarm()
    mock_coordinator.disarm_alarm.assert_called_once_with("ground_base_1")


async def test_alarm_arm_home(mock_coordinator: MagicMock) -> None:
    """Test alarm arm home."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_home()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "home")


async def test_alarm_arm_away(mock_coordinator: MagicMock) -> None:
    """Test alarm arm away."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_away()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "away")


async def test_alarm_arm_night(mock_coordinator: MagicMock) -> None:
    """Test alarm arm night."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_arm_night()
    mock_coordinator.set_mode.assert_called_once_with("ground_base_1", "schedule")


async def test_alarm_trigger(mock_coordinator: MagicMock) -> None:
    """Test alarm trigger."""
    device_info = mock_coordinator.data["ground_base_1"]
    alarm = EufyAlarmControlPanel(mock_coordinator, "ground_base_1", device_info)

    await alarm.async_alarm_trigger()
    mock_coordinator.trigger_alarm.assert_called_once_with("ground_base_1")
