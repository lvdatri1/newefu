"""Camera platform for the Eufy Custom Integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_STREAM_URL, DOMAIN
from .coordinator import EufyDataUpdateCoordinator
from .devices.base_device import EufyDeviceEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy camera entities."""
    coordinator: EufyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    entities: list[EufyCamera] = []
    if coordinator.data:
        for device_id, device_info in coordinator.data.items():
            if device_info.get("type") in ("camera", "doorbell"):
                entities.append(EufyCamera(coordinator, device_id, device_info))

    async_add_entities(entities)


class EufyCamera(EufyDeviceEntity, Camera):
    """Representation of a Eufy camera."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_motion_detection_enabled = False

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialize the Eufy camera."""
        EufyDeviceEntity.__init__(self, coordinator, device_id, device_info)
        Camera.__init__(self)

        self._attr_brand = "Eufy"
        self._attr_model = device_info.get("device_model")
        self._attr_serial_number = device_info.get("serial_number")

    @property
    def is_streaming(self) -> bool:
        """Return whether the camera is streaming."""
        data = self._get_device_data()
        if data:
            return data.get("state") == "streaming"
        return False

    @property
    def is_recording(self) -> bool:
        """Return whether the camera is recording."""
        data = self._get_device_data()
        if data:
            return data.get("state") == "recording"
        return False

    @property
    def motion_detection_enabled(self) -> bool:
        """Return whether motion detection is enabled."""
        return self._get_property("motion_detection", False)

    async def async_enable_motion_detection(self) -> None:
        """Enable motion detection."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = True
            data["properties"] = properties

    async def async_disable_motion_detection(self) -> None:
        """Disable motion detection."""
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = False
            data["properties"] = properties

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        return b""

    async def stream_source(self) -> str | None:
        """Return the source of the stream."""
        data = self._get_device_data()
        if data:
            return data.get(ATTR_STREAM_URL)
        return None
