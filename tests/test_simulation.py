"""End-to-end simulation: coordinator updates --> entity state changes.

Simulates real-world events (motion detection, doorbell press, mode
change, lock toggle) flowing through the coordinator to entities.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.eufy_custom_integration.alarm_control_panel import (
    EufyAlarmControlPanel,
)
from custom_components.eufy_custom_integration.binary_sensor import (
    EufyDoorbellPressSensor,
    EufyMotionSensor,
    EufyOnlineSensor,
)
from custom_components.eufy_custom_integration.camera import EufyCamera
from custom_components.eufy_custom_integration.lock import EufyLock
from custom_components.eufy_custom_integration.select import EufyModeSelect
from custom_components.eufy_custom_integration.sensor import (
    EufyBatterySensor,
    EufyWiFiSignalSensor,
)
from custom_components.eufy_custom_integration.switch import (
    EufyMotionDetectionSwitch,
)

# ---------------------------------------------------------------------------
# Helper — build all entities from a coordinator
# ---------------------------------------------------------------------------

def create_all_entities(
    coordinator: MagicMock,
) -> dict[str, Any]:
    """Instantiate every possible entity type for all devices in coordinator.

    Returns a dict mapping descriptive names to entity instances so
    the simulation can easily refer to them (e.g. sim["camera_motion"]).
    """
    entities: dict[str, Any] = {}
    data = coordinator.data or {}

    for device_id, info in data.items():
        dtype = info.get("type", "")

        if dtype in ("camera", "doorbell"):
            entities[f"{device_id}_motion_sensor"] = EufyMotionSensor(
                coordinator, device_id, info
            )
            entities[f"{device_id}_online_sensor"] = EufyOnlineSensor(
                coordinator, device_id, info
            )
            entities[f"{device_id}_battery"] = EufyBatterySensor(
                coordinator, device_id, info
            )
            entities[f"{device_id}_wifi"] = EufyWiFiSignalSensor(
                coordinator, device_id, info
            )
            entities[f"{device_id}_motion_switch"] = EufyMotionDetectionSwitch(
                coordinator, device_id, info
            )

        if dtype == "doorbell":
            entities[f"{device_id}_ring_sensor"] = EufyDoorbellPressSensor(
                coordinator, device_id, info
            )

        if dtype in ("camera", "doorbell"):
            entities[f"{device_id}_camera"] = EufyCamera(
                coordinator, device_id, info
            )

        if dtype == "ground_base":
            entities[f"{device_id}_alarm"] = EufyAlarmControlPanel(
                coordinator, device_id, info
            )
            entities[f"{device_id}_mode_select"] = EufyModeSelect(
                coordinator, device_id, info
            )

        if dtype == "smart_lock":
            entities[f"{device_id}_lock"] = EufyLock(
                coordinator, device_id, info
            )

    return entities


# ---------------------------------------------------------------------------
# Simulation scenarios
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_simulation_motion_detection_flow(mock_coordinator: MagicMock) -> None:
    """Simulate: motion detected on camera --> sensor turns on.

    Event:            coordinator.data["camera_1"]["properties"]["motion_detected"]
                      changes from False to True.

    Expected effect:  camera_1_motion_sensor.is_on goes False -> True.
    """
    sim = create_all_entities(mock_coordinator)
    motion = sim["camera_1_motion_sensor"]

    # --- initial state: no motion -----------------------------------------
    assert motion.is_on is False

    # --- simulate motion event --------------------------------------------
    mock_coordinator.data["camera_1"]["properties"]["motion_detected"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert motion.is_on is True

    # --- motion clears ----------------------------------------------------
    mock_coordinator.data["camera_1"]["properties"]["motion_detected"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert motion.is_on is False


@pytest.mark.asyncio
async def test_simulation_motion_detection_toggle_flow(
    mock_coordinator: MagicMock,
) -> None:
    """Simulate: user toggles motion detection switch.

    Event:            switch.async_turn_off() / async_turn_on()

    Expected effect:  switch.is_on follows toggle; camera motion_detection
                      property is updated.
    """
    sim = create_all_entities(mock_coordinator)
    sw = sim["camera_1_motion_switch"]

    assert sw.is_on is False

    await sw.async_turn_on()
    assert sw.is_on is True
    assert (
        mock_coordinator.data["camera_1"]["properties"]["motion_detection"] is True
    )

    await sw.async_turn_off()
    assert sw.is_on is False
    assert (
        mock_coordinator.data["camera_1"]["properties"]["motion_detection"] is False
    )


@pytest.mark.asyncio
async def test_simulation_doorbell_press_flow(mock_coordinator: MagicMock) -> None:
    """Simulate: doorbell pressed --> ring sensor activates.

    Event:            coordinator.data["doorbell_1"]["properties"]["ringing"]
                      changes from False to True.

    Expected effect:  doorbell_1_ring_sensor.is_on goes False -> True.
    """
    sim = create_all_entities(mock_coordinator)
    ring = sim["doorbell_1_ring_sensor"]

    assert ring.is_on is False

    mock_coordinator.data["doorbell_1"]["properties"]["ringing"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert ring.is_on is True

    mock_coordinator.data["doorbell_1"]["properties"]["ringing"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert ring.is_on is False


@pytest.mark.asyncio
async def test_simulation_lock_flow(mock_coordinator: MagicMock) -> None:
    """Simulate: lock-unlock cycle on a smart lock.

    Events:           async_lock() -> async_unlock()
                      coordinator push-lock -> jammed recovery.

    Expected effect:  is_locked, is_locking, is_unlocking, is_jammed
                      follow the correct sequence.
    """
    sim = create_all_entities(mock_coordinator)
    lock = sim["lock_1_lock"]

    # --- initial: locked --------------------------------------------------
    assert lock.is_locked is True
    assert lock.is_locking is False
    assert lock.is_unlocking is False
    assert lock.is_jammed is False

    # --- unlock -----------------------------------------------------------
    await lock.async_unlock()
    assert lock.is_locked is False
    assert lock.is_unlocking is True
    assert mock_coordinator.data["lock_1"]["properties"]["unlocking"] is True

    # --- finish unlock (simulate API callback) ----------------------------
    mock_coordinator.data["lock_1"]["properties"]["unlocking"] = False
    mock_coordinator.data["lock_1"]["properties"]["locked"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert lock.is_locked is False
    assert lock.is_unlocking is False

    # --- lock again -------------------------------------------------------
    await lock.async_lock()
    assert lock.is_locked is True
    assert lock.is_locking is True

    # --- finish lock ------------------------------------------------------
    mock_coordinator.data["lock_1"]["properties"]["locking"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert lock.is_locked is True
    assert lock.is_locking is False

    # --- jammed -----------------------------------------------------------
    mock_coordinator.data["lock_1"]["properties"]["jammed"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert lock.is_jammed is True

    # --- recover from jam -------------------------------------------------
    mock_coordinator.data["lock_1"]["properties"]["jammed"] = False
    mock_coordinator.data["lock_1"]["properties"]["locked"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert lock.is_jammed is False
    assert lock.is_locked is True


@pytest.mark.asyncio
async def test_simulation_alarm_mode_flow(mock_coordinator: MagicMock) -> None:
    """Simulate: security mode changes on ground base.

    Events:           select option changes (disarmed -> home -> away)
    """
    sim = create_all_entities(mock_coordinator)
    alarm = sim["ground_base_1_alarm"]
    select = sim["ground_base_1_mode_select"]

    assert select.current_option == "disarmed"
    assert alarm.state == "disarmed"

    # --- arm home ---------------------------------------------------------
    mock_coordinator.data["ground_base_1"]["properties"]["mode"] = "home"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert select.current_option == "home"
    assert alarm.state == "armed_home"

    # --- arm away ---------------------------------------------------------
    mock_coordinator.data["ground_base_1"]["properties"]["mode"] = "away"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert select.current_option == "away"
    assert alarm.state == "armed_away"

    # --- trigger alarm ----------------------------------------------------
    mock_coordinator.data["ground_base_1"]["state"] = "alarm_triggered"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert alarm.state == "triggered"

    # --- disarm -----------------------------------------------------------
    mock_coordinator.data["ground_base_1"]["state"] = "disarmed"
    mock_coordinator.data["ground_base_1"]["properties"]["mode"] = "disarmed"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert alarm.state == "disarmed"
    assert select.current_option == "disarmed"


@pytest.mark.asyncio
async def test_simulation_camera_streaming_flow(mock_coordinator: MagicMock) -> None:
    """Simulate: camera starts/stops streaming."""
    sim = create_all_entities(mock_coordinator)
    cam = sim["camera_1_camera"]

    assert cam.is_streaming is False
    assert cam.is_recording is False

    mock_coordinator.data["camera_1"]["state"] = "streaming"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert cam.is_streaming is True

    mock_coordinator.data["camera_1"]["state"] = "recording"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert cam.is_recording is True
    assert cam.is_streaming is False


@pytest.mark.asyncio
async def test_simulation_sensor_updates(mock_coordinator: MagicMock) -> None:
    """Simulate: battery and wifi signal level changes."""
    sim = create_all_entities(mock_coordinator)
    batt = sim["camera_1_battery"]
    wifi = sim["camera_1_wifi"]

    assert batt.native_value == 85
    assert wifi.native_value == -45

    mock_coordinator.data["camera_1"]["battery_level"] = 42
    mock_coordinator.data["camera_1"]["wifi_signal"] = -72
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)

    assert batt.native_value == 42
    assert wifi.native_value == -72


@pytest.mark.asyncio
async def test_simulation_online_status_changes(mock_coordinator: MagicMock) -> None:
    """Simulate: device goes offline then comes back."""
    sim = create_all_entities(mock_coordinator)
    online = sim["camera_1_online_sensor"]

    assert online.is_on is True
    assert online.available is True

    mock_coordinator.data["camera_1"]["is_online"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert online.is_on is False

    mock_coordinator.data["camera_1"]["is_online"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert online.is_on is True


@pytest.mark.asyncio
async def test_simulation_doorbell_motion_and_ring(
    mock_coordinator: MagicMock,
) -> None:
    """Simulate: doorbell detects motion while ringing.

    Demonstrates that multiple properties on the same device can be
    updated independently.
    """
    sim = create_all_entities(mock_coordinator)
    ring = sim["doorbell_1_ring_sensor"]
    motion = sim["doorbell_1_motion_sensor"]

    assert ring.is_on is False
    assert motion.is_on is False

    mock_coordinator.data["doorbell_1"]["properties"]["ringing"] = True
    mock_coordinator.data["doorbell_1"]["properties"]["motion_detected"] = True
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)

    assert ring.is_on is True
    assert motion.is_on is True

    mock_coordinator.data["doorbell_1"]["properties"]["ringing"] = False
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)

    assert ring.is_on is False
    assert motion.is_on is True


@pytest.mark.asyncio
async def test_simulation_camera_stream_source_flow(
    mock_coordinator: MagicMock,
) -> None:
    """Simulate: camera RTSP stream URL appears after wake."""
    sim = create_all_entities(mock_coordinator)
    cam = sim["camera_1_camera"]

    assert await cam.stream_source() == "rtsp://192.168.1.100:554/stream1"

    mock_coordinator.data["camera_1"]["stream_url"] = None
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert await cam.stream_source() is None

    mock_coordinator.data["camera_1"][
        "stream_url"
    ] = "rtsp://192.168.1.100:554/stream2"
    await mock_coordinator.async_set_updated_data(mock_coordinator.data)
    assert await cam.stream_source() == "rtsp://192.168.1.100:554/stream2"
