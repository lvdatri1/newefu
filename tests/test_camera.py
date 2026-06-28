"""
Tests for the Eufy Camera platform (camera.py).

================================================================================
 COVERAGE
================================================================================

 - Camera entity initialisation with correct name, unique_id, model
 - Supported features (stream)
 - Streaming state (is_streaming, is_recording)
 - Stream source URL retrieval
 - Motion detection enable/disable toggle
 - Camera image capture (placeholder)
 - Entity availability when coordinator data is missing
 - Doorbell treated as camera entity
"""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.camera import CameraEntityFeature

from custom_components.eufy_custom_integration.camera import EufyCamera


async def test_camera_initialization(mock_coordinator: MagicMock) -> None:
    """Verify camera entity is created with correct metadata.

    Checks name, unique_id, model, and manufacturer are populated
    from the device info dict.
    """
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.unique_id == "SN123456789"
    assert camera.name == "Front Door Camera"
    assert camera._attr_device_info["model"] == "T8111"
    assert camera._attr_device_info["manufacturer"] == "Eufy"


async def test_camera_supported_features(mock_coordinator: MagicMock) -> None:
    """Verify camera advertises stream support."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.supported_features == CameraEntityFeature.STREAM


async def test_camera_stream_source(mock_coordinator: MagicMock) -> None:
    """Verify stream_source() returns the RTSP URL from device data."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    source = await camera.stream_source()
    assert source == "rtsp://192.168.1.100:554/stream1"


async def test_camera_stream_source_none(mock_coordinator: MagicMock) -> None:
    """Verify stream_source() returns None when stream_url is absent."""
    device_info = dict(mock_coordinator.data["camera_1"])
    del device_info["stream_url"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    source = await camera.stream_source()
    assert source is None


async def test_camera_is_not_streaming(mock_coordinator: MagicMock) -> None:
    """Verify is_streaming and is_recording are False at idle."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.is_streaming is False
    assert camera.is_recording is False


async def test_camera_is_streaming(mock_coordinator: MagicMock) -> None:
    """Verify is_streaming is True when state is 'streaming'."""
    device_info = dict(mock_coordinator.data["camera_1"])
    device_info["state"] = "streaming"
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.is_streaming is True


async def test_camera_motion_detection(mock_coordinator: MagicMock) -> None:
    """Verify motion detection toggle works correctly."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.motion_detection_enabled is False

    await camera.async_enable_motion_detection()
    assert camera.motion_detection_enabled is True

    await camera.async_disable_motion_detection()
    assert camera.motion_detection_enabled is False


async def test_camera_camera_image(mock_coordinator: MagicMock) -> None:
    """Verify async_camera_image returns empty bytes (placeholder)."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    image = await camera.async_camera_image()
    assert image == b""


async def test_camera_available(mock_coordinator: MagicMock) -> None:
    """Verify camera is unavailable when coordinator data is None."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.available is True

    mock_coordinator.data = None
    assert camera.available is False


async def test_doorbell_camera_setup(mock_coordinator: MagicMock) -> None:
    """Verify doorbell devices are also exposed as Camera entities.

    Doorbells with cameras should support the same Camera interface.
    """
    device_info = mock_coordinator.data["doorbell_1"]
    camera = EufyCamera(mock_coordinator, "doorbell_1", device_info)

    assert camera.name == "Front Doorbell"
    assert camera._attr_model == "T8200"
    assert camera.unique_id == "SN987654321"
