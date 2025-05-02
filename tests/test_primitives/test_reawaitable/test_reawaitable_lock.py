import pytest
import anyio

from returns.primitives.reawaitable import (
    ReAwaitable,
    detect_async_context,
    _is_in_trio_context,
)


@pytest.mark.anyio
async def test_reawaitable_create_lock():
    """Test that ReAwaitable correctly creates the lock when needed."""
    async def sample_coroutine() -> str:
        return 'test'
    
    # Create ReAwaitable instance
    reawait = ReAwaitable(sample_coroutine())
    
    # The lock should be None initially
    assert reawait._lock is None
    
    # Await the coroutine once
    result1 = await reawait
    
    # The lock should be created
    assert reawait._lock is not None
    assert result1 == 'test'
    
    # Await again, should use the same lock
    result2 = await reawait
    assert result2 == 'test'


@pytest.mark.anyio
async def test_detect_async_context():
    """Test async context detection works correctly."""
    # When running with anyio, it should detect the backend correctly
    context = detect_async_context()
    assert context in ('asyncio', 'trio')


@pytest.mark.anyio
async def test_is_in_trio_context():
    """Test trio context detection."""
    # Since we might be running in either context,
    # we just check the function runs without errors
    result = _is_in_trio_context()
    # Result will depend on which backend anyio is using
    assert isinstance(result, bool)