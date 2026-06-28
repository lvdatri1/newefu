# Eufy Custom Integration

Home Assistant custom integration for Eufy security devices (cameras, doorbells, ground bases, smart locks, sensors).

## Features

- **Cameras** - View streams, motion detection, snapshots
- **Doorbells** - Stream, two-way audio, ring events
- **Ground Bases** - Security modes (home/away/schedule/custom/disarmed), alarm control panel
- **Smart Locks** - Lock/unlock, status monitoring
- **Sensors** - Battery level, WiFi signal strength, motion detection, online status
- **Switches** - Motion detection toggle
- **Select** - Security mode selection
- **Buttons** - Device wake-up
- **Binary Sensors** - Motion, connectivity, doorbell press

## Installation

### HACS (recommended)
1. Add this repo as a custom repository in HACS
2. Search for "Eufy Custom Integration" and install
3. Restart Home Assistant

### Manual
1. Copy `custom_components/eufy_custom_integration/` to your Home Assistant `custom_components/` directory
2. Restart Home Assistant
3. Add the integration via Settings → Devices & Services → Add Integration → "Eufy Custom Integration"
4. Enter your Eufy email, password, and country code

## Platforms

| Platform | Description |
|----------|-------------|
| `camera` | Camera streams and snapshots |
| `sensor` | Battery level and WiFi signal sensors |
| `binary_sensor` | Motion, connectivity, and doorbell ring sensors |
| `switch` | Motion detection toggle |
| `select` | Security mode selector (ground base) |
| `button` | Device wake-up button |
| `lock` | Smart lock control |
| `alarm_control_panel` | Ground base alarm panel |

## Testing

```bash
pytest tests/ -v
```

## License

MIT
