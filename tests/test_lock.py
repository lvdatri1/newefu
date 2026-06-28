"""Tests for the Eufy Lock platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.lock import EufyLock


async def test_lock_initialization(mock_coordinator: MagicMock) -> None:
    """Test lock initialization."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.name == "Front Door Lock"
    assert lock.unique_id == "SN555555555"


async def test_lock_is_locked(mock_coordinator: MagicMock) -> None:
    """Test lock is locked."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is True


async def test_lock_is_unlocked(mock_coordinator: MagicMock) -> None:
    """Test lock is unlocked."""
    device_info = dict(mock_coordinator.data["lock_1"])
    device_info["properties"] = {"locked": False}
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is False


async def test_lock_lock(mock_coordinator: MagicMock) -> None:
    """Test lock action."""
    device_info = dict(mock_coordinator.data["lock_1"])
    device_info["properties"] = {"locked": False}
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is False

    await lock.async_lock()
    assert lock.is_locked is True
    assert lock.is_locking is True


async def test_lock_unlock(mock_coordinator: MagicMock) -> None:
    """Test unlock action."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is True

    await lock.async_unlock()
    assert lock.is_locked is False
    assert lock.is_unlocking is True


async def test_lock_jammed(mock_coordinator: MagicMock) -> None:
    """Test lock jammed state."""
    device_info = dict(mock_coordinator.data["lock_1"])
    device_info["properties"] = {"jammed": True}
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_jammed is True
