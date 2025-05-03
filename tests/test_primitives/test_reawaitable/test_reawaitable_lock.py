import pytest
import anyio

from returns.primitives.reawaitable import (
    ReAwaitable,
    detect_async_context,
    _is_in_trio_context,
)


async def _test_coro() -> str:
    """Test coroutine for ReAwaitable tests."""
    return 'test'


@pytest.mark.anyio
async def test_reawaitable_lock_none_initially():
    """Test that ReAwaitable has no lock initially."""
    reawait = ReAwaitable(_test_coro())
    assert reawait._lock is None


@pytest.mark.anyio
async def test_reawaitable_creates_lock():
    """Test that ReAwaitable creates lock after first await."""
    reawait = ReAwaitable(_test_coro())
    await reawait
    assert reawait._lock is not None


@pytest.mark.anyio
async def test_reawait_twice():
    """Test awaiting the same ReAwaitable twice."""
    reawait = ReAwaitable(_test_coro())
    first: str = await reawait
    second: str = await reawait
    assert first == second == 'test'


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
    result: bool = _is_in_trio_context()
    # Result will depend on which backend anyio is using
    assert isinstance(result, bool)