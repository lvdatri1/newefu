# Eufy Custom Integration

[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.1-%2341BDF5.svg)](https://homeassistant.io)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)

Home Assistant custom integration for Eufy security devices — cameras, doorbells, ground bases (HomeBase), smart locks, and sensors.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Platforms](#platforms)
- [Services](#services)
- [Testing](#testing)
  - [Unit Tests (Mock)](#unit-tests-mock)
  - [Integration Tests (Real Device)](#integration-tests-real-device)
- [Development](#development)
- [Extending the Integration](#extending-the-integration)
- [License](#license)

---

## Features

| Device Type    | Entities                                                                 |
|----------------|--------------------------------------------------------------------------|
| **Camera**     | Camera (stream, snapshot, motion detection toggle)                       |
| **Doorbell**   | Camera + Doorbell Press binary sensor                                   |
| **Ground Base**| Alarm Control Panel + Security Mode selector + Online sensor            |
| **Smart Lock** | Lock (lock/unlock, status, jam detection)                                |
| **All**        | Battery sensor, WiFi signal sensor, Motion sensor, Online sensor, Wake button |

---

## Architecture

```
                        Eufy Cloud / API
                             |
                    EufyDataUpdateCoordinator
                   (poll + push, holds all state)
                             |
                     EufyDeviceManager
                 (HA device registry integration)
                             |
     +--------+--------+--------+--------+--------+--------+
     |        |        |        |        |        |        |
  Camera  Sensor  BinarySwitch  Select  Button   Lock  AlarmPanel
                        Sensor
```

### Key files

| File | Purpose |
|------|---------|
| `__init__.py` | Integration entry point, platform forwarding |
| `const.py` | All constants, config keys, events, services |
| `coordinator.py` | Data polling + command methods (set_mode, trigger, disarm) |
| `device_manager.py` | HA device registry management |
| `config_flow.py` | UI setup wizard (email, password, country code) |
| `devices/base_device.py` | Base entity class with device_info + helpers |
| `camera.py`, `sensor.py`, ... | Per-platform entity implementations |
| `services.yaml` | Custom service definitions for HA |
| `translations/` | Localized strings for the config flow |

### Data flow

1. User enters credentials via **config_flow.py** → creates a `ConfigEntry`.
2. **`__init__.py:async_setup_entry()`** creates the `EufyDataUpdateCoordinator` and performs an initial data refresh.
3. The coordinator polls `_fetch_devices()` at a configurable interval (default 30s).
4. **`EufyDeviceManager`** registers each device in the HA device registry.
5. Each platform (`camera.py`, `sensor.py`, etc.) creates entities that subscribe to coordinator updates.
6. Entities read state from `coordinator.data[device_id]` and map it to HA properties.

---

## Installation

### HACS (recommended)
1. Add this repo as a custom repository in HACS
2. Search for "Eufy (lvdatri)" and install
3. Restart Home Assistant

### Manual
1. Copy `custom_components/lvdatri_eufy/` to your Home Assistant `custom_components/` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services → Add Integration → "Eufy (lvdatri)"
4. Enter your Eufy email, password, and country code

## Platforms

| Platform             | Entity              | Device Type Filter    | Description                                       |
|----------------------|---------------------|-----------------------|---------------------------------------------------|
| `camera`             | `EufyCamera`        | camera, doorbell      | Live stream, snapshot, motion detection toggle    |
| `sensor`             | `EufyBatterySensor` | any                   | Battery level percentage (0-100%)                 |
| `sensor`             | `EufyWiFiSignalSensor` | any                | WiFi RSSI in dBm                                  |
| `binary_sensor`      | `EufyMotionSensor`  | camera, doorbell      | Motion detected (on/off)                          |
| `binary_sensor`      | `EufyOnlineSensor`  | any                   | Device connectivity status                        |
| `binary_sensor`      | `EufyDoorbellPressSensor` | doorbell        | Doorbell ringing (on/off)                         |
| `switch`             | `EufyMotionDetectionSwitch` | camera, doorbell | Toggle motion detection                     |
| `select`             | `EufyModeSelect`    | ground_base           | Security mode: home, away, schedule, custom, disarm |
| `button`             | `EufyWakeUpButton`  | camera, doorbell      | Wake device from standby                          |
| `lock`               | `EufyLock`          | smart_lock            | Lock/unlock with jam detection                    |
| `alarm_control_panel`| `EufyAlarmControlPanel` | ground_base       | Arm home, arm away, arm night, disarm, trigger   |

---

## Services

| Service              | Description                | Target Entity               |
|----------------------|----------------------------|------------------------------|
| `set_mode`           | Set ground base mode       | `select.eufy_*_security_mode` |
| `start_stream`       | Start camera stream        | `camera.eufy_*`              |
| `stop_stream`        | Stop camera stream         | `camera.eufy_*`              |
| `trigger_alarm`      | Manually trigger alarm     | `alarm_control_panel.eufy_*` |
| `disarm_alarm`       | Disarm the alarm           | `alarm_control_panel.eufy_*` |

---

## Testing

The project includes two tiers of tests:

### Unit Tests (Mock)

Runs against simulated device data — no real hardware needed.

```bash
# Run all unit tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_camera.py -v

# Run a specific test
pytest tests/test_camera.py::test_camera_initialization -v

# Run with coverage report
pytest tests/ --cov=custom_components.lvdatri_eufy -v
```

### Integration Tests (Real Device)

Runs against your real Eufy cloud account. **Set these environment variables:**

```bash
# Replace with your Eufy account credentials
export EUFY_USERNAME="your@email.com"
export EUFY_PASSWORD="your_secure_password"

# Optional: override poll interval
# export EUFY_POLL_INTERVAL="30"

# Run integration tests (requires --run-real flag)
pytest tests/ -v --run-real
```

> **⚠️ Security note:** Never commit your credentials to git. The `.gitignore` already excludes `.env` files. Use a `.env` file with `source .env` for local development.

#### Example `.env` file (do not commit):

```bash
EUFY_USERNAME=your@email.com
EUFY_PASSWORD=your_secure_password
```

### Test Structure

```
tests/
├── __init__.py                     # Marks as package
├── conftest.py                     # Fixtures: mock data, mock coordinator,
│                                   #   mock hass, real coordinator (--run-real)
├── test_alarm_control_panel.py     # EufyAlarmControlPanel tests
├── test_base_device.py             # EufyDeviceEntity base class tests
├── test_binary_sensor.py           # Motion, Online, DoorbellPress sensors
├── test_button.py                  # EufyWakeUpButton tests
├── test_camera.py                  # EufyCamera tests (stream, motion, etc.)
├── test_config_flow.py             # Config flow wizard tests
├── test_coordinator.py             # Coordinator fetch + command tests
├── test_device_manager.py          # Device registry tests
├── test_integration_ha.py          # Full HA lifecycle (setup → update → unload)
├── test_lock.py                    # EufyLock tests (lock/unlock/jam)
├── test_select.py                  # EufyModeSelect tests
├── test_sensor.py                  # Battery + WiFi signal sensor tests
├── test_simulation.py              # End-to-end event-flow simulations
└── test_switch.py                  # Motion detection switch tests
```

---

## Development

### Prerequisites

- Python 3.12+
- Home Assistant 2024.1+ (for runtime testing)
- `pyeufysecurity` library (for cloud API access)

### Setup

```bash
# Clone the repository
git clone https://github.com/lvdatri1/newefu.git
cd newefu

# (Optional) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install pytest pytest-cov
```

### Adding a new device type

1. Add a `DEVICE_TYPE_*` constant in `const.py`.
2. Add sample data in `coordinator.py:_fetch_devices()`.
3. Create a platform file (e.g., `cover.py`) or extend an existing one.
4. Register the platform in `__init__.py:PLATFORMS`.
5. Add the `async_setup_entry()` function to the platform file.
6. Write tests in `tests/test_<platform>.py`.

### Adding a new sensor

1. Subclass `EufyDeviceEntity` or `EufySensor` in the appropriate platform file.
2. Override `native_value` to read from `_get_device_data()` or `_get_property()`.
3. Set `_attr_device_class` and `_attr_native_unit_of_measurement`.
4. Instantiate in the platform's `async_setup_entry()`.
5. Write tests following the pattern in `test_sensor.py`.

---

## Extending the Integration

This integration is designed to be easily extended by AI agents and developers. Key extension points:

| Extension Point | File | What to Do |
|-----------------|------|------------|
| New device type | `const.py`, `coordinator.py` | Add type constant + sample data |
| New platform    | `__init__.py`, new `<platform>.py` | Add to PLATFORMS, create platform file |
| New sensor      | `sensor.py` or `binary_sensor.py` | Subclass + override native_value |
| New command     | `coordinator.py` | Add method + wire in the platform |
| New service     | `services.yaml`, `coordinator.py` | Define schema + implement handler |
| Config option   | `config_flow.py`, `const.py` | Add field + constant |

For AI agents: Read the docstring at the top of each Python file — it contains the complete architectural context, data flow, and extension guide.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
