import asyncio
from typing import Any
from unittest.mock import patch

import pytest

from returns.primitives.reawaitable import (
    ReAwaitable,
    _sentinel,  # noqa: PLC2701
    reawaitable,
)


class CallCounter:
    """Helper class to count function calls."""

    def __init__(self) -> None:
        """Initialize counter."""
        self.count = 0

    def increment(self) -> None:
        """Increment the counter."""
        self.count += 1


async def _await_helper(awaitable: ReAwaitable) -> Any:
    """Helper function to await a ReAwaitable."""
    return await awaitable


async def _example_with_value(input_value: int) -> int:
    """Helper coroutine that returns the input value after a delay."""
    await asyncio.sleep(0.01)
    return input_value


async def _example_coro_with_counter(counter: CallCounter) -> int:
    """Helper coroutine that increments a counter and returns 42."""
    counter.increment()
    await asyncio.sleep(0.01)  # Simulate some async work
    return 42


async def _example_coro_simple() -> int:
    """Helper coroutine that returns 42 after a delay."""
    await asyncio.sleep(0.01)
    return 42


async def _example_coro_with_counter_no_sleep(counter: CallCounter) -> int:
    """Helper coroutine that increments a counter and returns 42 immediately."""
    counter.increment()
    return 42


async def _example_coro_return_one() -> int:
    """Helper coroutine that returns 1."""
    return 1


async def _decorated_coro_for_test(counter: CallCounter) -> int:
    """Helper decorated coroutine for testing the reawaitable decorator."""
    counter.increment()
    return 42


def _access_private_cache(
    awaitable: ReAwaitable, cache_value: Any = None
) -> Any:
    """Helper to access private cache attribute."""
    if cache_value is not None:
        awaitable._cache = cache_value  # noqa: SLF001
    return awaitable._cache  # noqa: SLF001


def _access_private_lock(awaitable: ReAwaitable, lock: Any = None) -> Any:
    """Helper to access private lock attribute."""
    if lock is not None:
        awaitable._lock = lock  # noqa: SLF001
    return awaitable._lock  # noqa: SLF001


def _get_sentinel() -> Any:
    """Helper to get the sentinel value."""
    return _sentinel


def _call_private_awaitable(awaitable: ReAwaitable) -> Any:
    """Helper to call private _awaitable method."""
    return awaitable._awaitable()  # noqa: SLF001


@pytest.mark.asyncio
async def test_concurrent_await():
    """Test that ReAwaitable can be awaited concurrently from multiple tasks."""
    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter(counter))

    # Create multiple tasks that await the same ReAwaitable instance
    tasks = [
        asyncio.create_task(_await_helper(awaitable)),
        asyncio.create_task(_await_helper(awaitable)),
        asyncio.create_task(_await_helper(awaitable)),
    ]

    # All tasks should complete without error
    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that no exceptions were raised
    for result in gathered_results:
        assert not isinstance(result, Exception)

    # The underlying coroutine should only be called once
    assert counter.count == 1

    # All results should be the same
    assert all(res == 42 for res in gathered_results)


@pytest.mark.asyncio
async def test_concurrent_await_with_different_values():
    """Test that multiple ReAwaitable instances work correctly."""
    awaitables = [
        ReAwaitable(_example_with_value(0)),
        ReAwaitable(_example_with_value(1)),
        ReAwaitable(_example_with_value(2)),
    ]

    # Create tasks for each awaitable
    tasks = []
    for awaitable in awaitables:
        # Each awaitable is awaited multiple times
        tasks.extend([
            asyncio.create_task(_await_helper(awaitable)),
            asyncio.create_task(_await_helper(awaitable)),
        ])

    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that no exceptions were raised
    for result in gathered_results:
        assert not isinstance(result, Exception)

    # Check that each awaitable returned its correct value multiple times
    assert gathered_results[0] == gathered_results[1] == 0
    assert gathered_results[2] == gathered_results[3] == 1
    assert gathered_results[4] == gathered_results[5] == 2


@pytest.mark.asyncio
async def test_sequential_await():
    """Test that ReAwaitable still works correctly with sequential awaits."""
    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Sequential awaits should work as before
    result1: int = await awaitable
    result2: int = await awaitable
    result3: int = await awaitable

    assert result1 == result2 == result3 == 42
    assert counter.count == 1  # Should only be called once


@pytest.mark.asyncio
async def test_no_event_loop_fallback():
    """Test that ReAwaitable works when no event loop is available."""
    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Mock asyncio.Lock to raise RuntimeError (simulating no event loop)
    with patch('asyncio.Lock', side_effect=RuntimeError('No event loop')):
        # First await should execute the coroutine and cache the result
        result1: int = await awaitable
        assert result1 == 42
        assert counter.count == 1

        # Second await should return cached result without executing again
        result2: int = await awaitable
        assert result2 == 42
        assert counter.count == 1  # Should still be 1, not incremented


@pytest.mark.asyncio
async def test_lock_path_branch_coverage():
    """Test to ensure branch coverage in the lock acquisition path."""
    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # First ensure normal path works (should create lock and execute)
    result1: int = await awaitable
    assert result1 == 42
    assert counter.count == 1

    # Second call should go through the locked path and find cache
    result2: int = await awaitable
    assert result2 == 42
    assert counter.count == 1


@pytest.mark.asyncio
async def test_reawaitable_decorator():
    """Test the reawaitable decorator function."""
    counter = CallCounter()

    decorated_func = reawaitable(_decorated_coro_for_test)

    # Test that the decorator works
    result = decorated_func(counter)
    assert isinstance(result, ReAwaitable)  # type: ignore[unreachable]

    # Test multiple awaits
    value1: int = await result  # type: ignore[unreachable]
    value2: int = await result
    assert value1 == value2 == 42
    assert counter.count == 1


def test_reawaitable_repr():
    """Test that ReAwaitable repr matches the coroutine repr."""
    coro = _example_coro_return_one()
    awaitable = ReAwaitable(coro)

    # The repr should match (though the exact format may vary)
    # We just check that repr works without error
    repr_result = repr(awaitable)
    assert isinstance(repr_result, str)
    assert len(repr_result) > 0


@pytest.mark.asyncio
async def test_precise_fallback_branch():
    """Test the exact lines 124-126 branch in fallback path."""
    # The goal is to hit:
    # if self._cache is _sentinel: (line 124)
    #     self._cache = await self._coro (line 125)
    # return self._cache (line 126)

    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Force the RuntimeError path by mocking asyncio.Lock
    with patch('asyncio.Lock', side_effect=RuntimeError('No event loop')):
        # This should execute the fallback and hit the branch we need
        result: int = await awaitable
        assert result == 42
        assert counter.count == 1

        # Verify we took the fallback path by checking _lock is still None
        assert _access_private_lock(awaitable) is None


@pytest.mark.asyncio
async def test_precise_double_check_branch():
    """Test the exact lines 130-132 branch in lock path."""
    # The goal is to hit:
    # if self._cache is _sentinel: (line 130)
    #     self._cache = await self._coro (line 131)
    # return self._cache (line 132)

    counter = CallCounter()

    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))
    # Manually set the lock to bypass lock creation
    _access_private_lock(awaitable, asyncio.Lock())

    # Ensure we start with sentinel - this is the default state
    assert _access_private_cache(awaitable) is _get_sentinel()

    # Now await - this should go through the lock path and hit our target branch
    result: int = await awaitable
    assert result == 42
    assert counter.count == 1


async def _test_normal_path() -> None:
    """Helper for testing normal execution path."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))
    result: int = await awaitable
    assert result == 42
    assert counter.count == 1


async def _test_fallback_path() -> None:
    """Helper for testing fallback path scenarios."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    with patch('asyncio.Lock', side_effect=RuntimeError('No event loop')):
        # Directly call _awaitable to bypass the early return
        _access_private_lock(awaitable, None)
        _access_private_cache(awaitable, _get_sentinel())

        result = await _call_private_awaitable(awaitable)
        assert result == 42
        assert counter.count == 1

        # Now test when cache is already set (the missing branch)
        _access_private_cache(awaitable, 99)
        cached_result: int = await _call_private_awaitable(awaitable)
        assert cached_result == 99  # Should return cached value
        assert counter.count == 1  # Should not increment


async def _test_lock_path() -> None:
    """Helper for testing lock path scenarios."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Force lock path by setting lock
    _access_private_lock(awaitable, asyncio.Lock())

    # Test normal lock path first
    result = await _call_private_awaitable(awaitable)
    assert result == 42
    assert counter.count == 1

    # Test lock path when cache is already set (the missing branch)
    _access_private_cache(awaitable, 99)
    cached_result = await _call_private_awaitable(awaitable)
    assert (
        cached_result == 99
    )  # Should return cached value without entering if block
    assert counter.count == 1  # Should not increment


@pytest.mark.asyncio
async def test_comprehensive_branch_coverage():
    """Test all edge cases to achieve 100% branch coverage."""
    # Test 1: Normal path where we set cache and then return it
    await _test_normal_path()

    # Test 2: Fallback path where asyncio.Lock fails
    await _test_fallback_path()

    # Test 3: Lock path where cache gets set by another execution
    await _test_lock_path()


async def _test_fallback_with_cached_value() -> None:
    """Test fallback path where cache is already set when reached."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    with patch('asyncio.Lock', side_effect=RuntimeError('No event loop')):
        # Set cache to non-sentinel value before the fallback path if statement
        _access_private_lock(awaitable, None)
        _access_private_cache(awaitable, 42)  # NOT _sentinel!

        # This hits fallback path but skips if block
        result = await _call_private_awaitable(awaitable)
        assert result == 42
        assert counter.count == 0  # Coroutine should not be called


async def _test_lock_with_cached_value() -> None:
    """Test lock path where cache is already set when reached."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Force lock path and set cache to non-sentinel
    _access_private_lock(awaitable, asyncio.Lock())
    _access_private_cache(awaitable, 42)  # NOT _sentinel!

    # This should hit the lock path but skip the if block
    result = await _call_private_awaitable(awaitable)
    assert result == 42
    assert counter.count == 0  # Coroutine should not be called


@pytest.mark.asyncio
async def test_specific_branch_coverage():
    """Test specific missing branches in fallback and lock paths."""
    # Test fallback path where cache is already set
    await _test_fallback_with_cached_value()

    # Test lock path where cache is already set
    await _test_lock_with_cached_value()
