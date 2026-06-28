"""Constants for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Final

import logging

LOGGER = logging.getLogger(__package__)

DOMAIN: Final = "eufy_custom_integration"
MANUFACTURER: Final = "Eufy"

CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_DEVICE_TYPE: Final = "device_type"
CONF_POLL_INTERVAL: Final = "poll_interval"

DEFAULT_PORT: Final = 5222
DEFAULT_POLL_INTERVAL: Final = 30

DEVICE_TYPE_CAMERA: Final = "camera"
DEVICE_TYPE_DOORBELL: Final = "doorbell"
DEVICE_TYPE_GROUND_BASE: Final = "ground_base"
DEVICE_TYPE_SMART_LOCK: Final = "smart_lock"
DEVICE_TYPE_SENSOR: Final = "sensor"
DEVICE_TYPE_SWITCH: Final = "switch"
DEVICE_TYPE_BUTTON: Final = "button"
DEVICE_TYPE_SELECT: Final = "select"

EVENT_MOTION_DETECTED: Final = "eufy_motion_detected"
EVENT_DOORBELL_RING: Final = "eufy_doorbell_ring"
EVENT_ALARM_TRIGGERED: Final = "eufy_alarm_triggered"

ATTR_DEVICE_ID: Final = "device_id"
ATTR_DEVICE_NAME: Final = "device_name"
ATTR_DEVICE_MODEL: Final = "device_model"
ATTR_SERIAL_NUMBER: Final = "serial_number"
ATTR_BATTERY_LEVEL: Final = "battery_level"
ATTR_WIFI_SIGNAL: Final = "wifi_signal"
ATTR_STREAM_URL: Final = "stream_url"
ATTR_IS_ONLINE: Final = "is_online"
ATTR_LAST_EVENT: Final = "last_event"
ATTR_ARMED: Final = "armed"
ATTR_MODE: Final = "mode"
ATTR_STATE: Final = "state"

SERVICE_SET_MODE: Final = "set_mode"
SERVICE_START_STREAM: Final = "start_stream"
SERVICE_STOP_STREAM: Final = "stop_stream"
SERVICE_TRIGGER_ALARM: Final = "trigger_alarm"
SERVICE_DISARM_ALARM: Final = "disarm_alarm"

MODE_HOME: Final = "home"
MODE_AWAY: Final = "away"
MODE_SCHEDULE: Final = "schedule"
MODE_CUSTOM: Final = "custom"
MODE_DISARMED: Final = "disarmed"
