"""
Constants for the Eufy Custom Integration.

================================================================================
 USAGE
================================================================================

 All integrations constants are defined here to avoid magic strings and to
 provide a single source of truth for configuration keys, event names,
 service names, attributes, and device types.

 To add a new device type:
   1. Add a DEVICE_TYPE_* constant here.
   2. Add the type to coordinator._fetch_devices().
   3. Create or update the relevant platform file.

 To add a new service:
   1. Add a SERVICE_* constant here.
   2. Implement the method in EufyDataUpdateCoordinator.
   3. Add the service definition to services.yaml.
   4. Register the service in the platform's async_setup_entry().

 To add a new attribute:
   1. Add an ATTR_* constant here.
   2. Include it in the device data dict returned by _fetch_devices().
   3. Expose it in the relevant entity class.
"""

from __future__ import annotations

from typing import Final

import logging

# -----------------------------------------------------------------------
# LOGGING
# Use LOGGER throughout the integration (e.g. LOGGER.debug(...)).
# Log level is controlled by HA's built-in logger integration.
# -----------------------------------------------------------------------
LOGGER = logging.getLogger(__package__)

# -----------------------------------------------------------------------
# DOMAIN & MANUFACTURER
# -----------------------------------------------------------------------
DOMAIN: Final = "lvdatri_eufy"
MANUFACTURER: Final = "Eufy"

# -----------------------------------------------------------------------
# CONFIGURATION KEYS
# Used in config_flow.py and coordinator.py for user-provided settings.
# -----------------------------------------------------------------------
CONF_USERNAME: Final = "username"
CONF_PASSWORD: Final = "password"
CONF_COUNTRY: Final = "country"
CONF_DEVICE_TYPE: Final = "device_type"
CONF_POLL_INTERVAL: Final = "poll_interval"

# -----------------------------------------------------------------------
# DEFAULTS
# Sensible defaults for optional configuration values.
# -----------------------------------------------------------------------
DEFAULT_POLL_INTERVAL: Final = 30

# -----------------------------------------------------------------------
# DEVICE TYPES
# Maps 1:1 to the "type" key in device data from the coordinator.
# Used by each platform's async_setup_entry() to filter devices.
# -----------------------------------------------------------------------
DEVICE_TYPE_CAMERA: Final = "camera"
DEVICE_TYPE_DOORBELL: Final = "doorbell"
DEVICE_TYPE_GROUND_BASE: Final = "ground_base"
DEVICE_TYPE_SMART_LOCK: Final = "smart_lock"
DEVICE_TYPE_SENSOR: Final = "sensor"
DEVICE_TYPE_SWITCH: Final = "switch"
DEVICE_TYPE_BUTTON: Final = "button"
DEVICE_TYPE_SELECT: Final = "select"

# -----------------------------------------------------------------------
# EVENTS
# Fired by the coordinator when device state changes.
# Listeners subscribe via hass.bus.async_listen().
# -----------------------------------------------------------------------
EVENT_MOTION_DETECTED: Final = "eufy_motion_detected"
EVENT_DOORBELL_RING: Final = "eufy_doorbell_ring"
EVENT_ALARM_TRIGGERED: Final = "eufy_alarm_triggered"

# -----------------------------------------------------------------------
# ATTRIBUTES
# Keys used in the device data dictionary and exposed as entity attributes.
# -----------------------------------------------------------------------
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

# -----------------------------------------------------------------------
# SERVICES
# Service names exposed to HA. Must match entries in services.yaml.
# -----------------------------------------------------------------------
SERVICE_SET_MODE: Final = "set_mode"
SERVICE_START_STREAM: Final = "start_stream"
SERVICE_STOP_STREAM: Final = "stop_stream"
SERVICE_TRIGGER_ALARM: Final = "trigger_alarm"
SERVICE_DISARM_ALARM: Final = "disarm_alarm"

# -----------------------------------------------------------------------
# SECURITY MODES
# Valid values for the ground base security mode selector.
# Used by select.py and alarm_control_panel.py.
# -----------------------------------------------------------------------
MODE_HOME: Final = "home"
MODE_AWAY: Final = "away"
MODE_SCHEDULE: Final = "schedule"
MODE_CUSTOM: Final = "custom"
MODE_DISARMED: Final = "disarmed"
