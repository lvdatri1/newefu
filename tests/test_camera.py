"""Tests for the Eufy Camera platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.components.camera import CameraEntityFeature

from custom_components.eufy_custom_integration.camera import EufyCamera


async def test_camera_initialization(mock_coordinator: MagicMock) -> None:
    """Test camera entity initialization."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.unique_id == "SN123456789"
    assert camera.name == "Front Door Camera"
    assert camera._attr_device_info["model"] == "T8111"
    assert camera._attr_device_info["manufacturer"] == "Eufy"


async def test_camera_supported_features(mock_coordinator: MagicMock) -> None:
    """Test camera supported features."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.supported_features == CameraEntityFeature.STREAM


async def test_camera_stream_source(mock_coordinator: MagicMock) -> None:
    """Test camera stream source."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    source = await camera.stream_source()
    assert source == "rtsp://192.168.1.100:554/stream1"


async def test_camera_stream_source_none(mock_coordinator: MagicMock) -> None:
    """Test camera stream source when no stream URL."""
    device_info = mock_coordinator.data["camera_1"]
    del device_info["stream_url"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    source = await camera.stream_source()
    assert source is None


async def test_camera_is_not_streaming(mock_coordinator: MagicMock) -> None:
    """Test camera streaming state."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.is_streaming is False
    assert camera.is_recording is False


async def test_camera_is_streaming(mock_coordinator: MagicMock) -> None:
    """Test camera streaming state when streaming."""
    device_info = dict(mock_coordinator.data["camera_1"])
    device_info["state"] = "streaming"
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.is_streaming is True


async def test_camera_motion_detection(mock_coordinator: MagicMock) -> None:
    """Test camera motion detection toggle."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.motion_detection_enabled is False

    await camera.async_enable_motion_detection()
    assert camera.motion_detection_enabled is True

    await camera.async_disable_motion_detection()
    assert camera.motion_detection_enabled is False


async def test_camera_camera_image(mock_coordinator: MagicMock) -> None:
    """Test camera image."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    image = await camera.async_camera_image()
    assert image == b""


async def test_camera_available(mock_coordinator: MagicMock) -> None:
    """Test camera availability."""
    device_info = mock_coordinator.data["camera_1"]
    camera = EufyCamera(mock_coordinator, "camera_1", device_info)

    assert camera.available is True

    mock_coordinator.data = None
    assert camera.available is False


async def test_doorbell_camera_setup(mock_coordinator: MagicMock) -> None:
    """Test doorbell camera setup."""
    device_info = mock_coordinator.data["doorbell_1"]
    camera = EufyCamera(mock_coordinator, "doorbell_1", device_info)

    assert camera.name == "Front Doorbell"
    assert camera._attr_model == "T8200"
    assert camera.unique_id == "SN987654321"
