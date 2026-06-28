"""
Camera platform for the Eufy Custom Integration.

================================================================================
 ROLE
================================================================================

 Provides the Camera entity for Eufy cameras and doorbells (doorbells with
 cameras are exposed as Camera entities). Supports:
   - Still image capture (async_camera_image)
   - RTSP streaming (stream_source)
   - Motion detection toggle (async_enable/disable_motion_detection)

================================================================================
 DATA FLOW
================================================================================

 async_setup_entry()
   -> reads coordinator data, filters for type "camera" / "doorbell"
   -> creates EufyCamera entities
   -> async_add_entities() registers them with HA

 Each EufyCamera reads its state from coordinator.data[device_id]:
   - is_streaming  <- state == "streaming"
   - is_recording  <- state == "recording"
   - stream_url    <- stream_url in device data
   - motion_detection <- properties.motion_detection

================================================================================
 EXTENSION POINTS
================================================================================

 To add camera-specific features:
   1. Add a property to _get_device_data() in the coordinator.
   2. Expose it via a property on EufyCamera.
   3. Add the relevant feature flag to _attr_supported_features.
"""

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
    """Set up Eufy camera entities from a config entry.

    Creates a EufyCamera for every device whose type is "camera" or
    "doorbell". Doorbells are exposed as cameras because they support
    the same streaming/image API.

    Args:
        hass: HomeAssistant instance.
        entry: The ConfigEntry for this integration.
        async_add_entities: HA callback to register new entities.
    """
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
    """Representation of a Eufy camera or doorbell camera.

    Combines HA's Camera entity with the EufyDeviceEntity base for
    coordinator integration. Supports streaming and motion detection.

    Attributes:
        _attr_brand:            Always "Eufy".
        _attr_model:            Device model number (e.g. T8111).
        _attr_supported_features: Flags for stream support.

    Usage:
        Accessible as a standard HA camera entity. Stream URL is
        read from the coordinator's device data.
    """

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_motion_detection_enabled = False

    def __init__(
        self,
        coordinator: EufyDataUpdateCoordinator,
        device_id: str,
        device_info: dict[str, Any],
    ) -> None:
        """Initialise the Eufy camera.

        Args:
            coordinator: The data coordinator.
            device_id:   The Eufy device ID.
            device_info: The device data dict.
        """
        EufyDeviceEntity.__init__(self, coordinator, device_id, device_info)
        Camera.__init__(self)

        self._attr_brand = "Eufy"
        self._attr_model = device_info.get("device_model")
        self._attr_serial_number = device_info.get("serial_number")

    # ------------------------------------------------------------------
    # STATE PROPERTIES
    # ------------------------------------------------------------------

    @property
    def is_streaming(self) -> bool:
        """Return True if the camera is currently streaming video."""
        data = self._get_device_data()
        if data:
            return data.get("state") == "streaming"
        return False

    @property
    def is_recording(self) -> bool:
        """Return True if the camera is currently recording."""
        data = self._get_device_data()
        if data:
            return data.get("state") == "recording"
        return False

    @property
    def motion_detection_enabled(self) -> bool:
        """Return True if motion detection is active.

        Reads from the device's properties dict.
        """
        return self._get_property("motion_detection", False)

    # ------------------------------------------------------------------
    # COMMANDS
    # ------------------------------------------------------------------

    async def async_enable_motion_detection(self) -> None:
        """Enable motion detection on the camera.

        Updates the local state and notifies HA of the change.
        The actual API call would go here (currently local-only).
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = True
            data["properties"] = properties

    async def async_disable_motion_detection(self) -> None:
        """Disable motion detection on the camera.

        Updates the local state and notifies HA of the change.
        """
        data = self._get_device_data()
        if data:
            properties = data.get("properties", {})
            properties["motion_detection"] = False
            data["properties"] = properties

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera.

        Called by HA to generate the preview thumbnail. Currently
        returns an empty bytes object; replace with actual frame
        capture from the Eufy API.

        Args:
            width:  Desired image width (ignored currently).
            height: Desired image height (ignored currently).

        Returns:
            JPEG/PNG bytes of the camera image, or None on failure.
        """
        return b""

    async def stream_source(self) -> str | None:
        """Return the RTSP stream URL for this camera.

        The URL is read from the coordinator's device data.
        HA uses this to feed into the stream component for live viewing.

        Returns:
            The RTSP URL string, or None if not available.
        """
        data = self._get_device_data()
        if data:
            return data.get(ATTR_STREAM_URL)
        return None
