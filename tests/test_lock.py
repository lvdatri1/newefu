"""
Tests for the Eufy Lock platform (lock.py).

================================================================================
 COVERAGE
================================================================================

 - Lock entity initialisation (name, unique_id)
 - Lock is_locked state from properties.locked
 - Lock is_unlocked state when locked=False
 - Lock command (async_lock) sets locked=True, locking=True
 - Unlock command (async_unlock) sets locked=False, unlocking=True
 - Lock jammed state from properties.jammed
"""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eufy_custom_integration.lock import EufyLock


async def test_lock_initialization(mock_coordinator: MagicMock) -> None:
    """Verify lock entity is created with correct metadata."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.name == "Front Door Lock"
    assert lock.unique_id == "SN555555555"


async def test_lock_is_locked(mock_coordinator: MagicMock) -> None:
    """Verify is_locked returns True when properties.locked is True."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is True


async def test_lock_is_unlocked(mock_coordinator: MagicMock) -> None:
    """Verify is_locked returns False when properties.locked is False."""
    mock_coordinator.data["lock_1"]["properties"]["locked"] = False
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is False


async def test_lock_lock(mock_coordinator: MagicMock) -> None:
    """Verify async_lock sets locked=True and locking=True."""
    mock_coordinator.data["lock_1"]["properties"]["locked"] = False
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is False

    await lock.async_lock()
    assert lock.is_locked is True
    assert lock.is_locking is True


async def test_lock_unlock(mock_coordinator: MagicMock) -> None:
    """Verify async_unlock sets locked=False and unlocking=True."""
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_locked is True

    await lock.async_unlock()
    assert lock.is_locked is False
    assert lock.is_unlocking is True


async def test_lock_jammed(mock_coordinator: MagicMock) -> None:
    """Verify is_jammed returns True when properties.jammed is True."""
    mock_coordinator.data["lock_1"]["properties"]["jammed"] = True
    device_info = mock_coordinator.data["lock_1"]
    lock = EufyLock(mock_coordinator, "lock_1", device_info)

    assert lock.is_jammed is True
