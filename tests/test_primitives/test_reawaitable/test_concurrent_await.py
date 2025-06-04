import asyncio
import logging
import types
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


class _ThreadingLockWrapper:  # noqa: WPS431
    """Wrapper for threading lock to test cache branch."""

    def __init__(
        self, lock: Any, awaitable: ReAwaitable, cache_value: int = 99
    ) -> None:
        self._lock = lock
        self._first_acquire = True
        self._awaitable = awaitable
        self._cache_value = cache_value

    def acquire(self) -> None:
        self._lock.acquire()
        # Simulate another thread setting cache while we have the lock
        if self._first_acquire:
            self._first_acquire = False
            _access_private_cache(self._awaitable, self._cache_value)

    def release(self) -> None:
        self._lock.release()

    def __enter__(self) -> '_ThreadingLockWrapper':
        self.acquire()
        return self

    def __exit__(self, *args: object) -> None:
        self.release()


class _AsyncLockWrapper:  # noqa: WPS431
    """Wrapper for async lock to test cache branch."""

    def __init__(
        self, lock: Any, awaitable: ReAwaitable, cache_value: int = 99
    ) -> None:
        self._lock = lock
        self._first_acquire = True
        self._awaitable = awaitable
        self._cache_value = cache_value

    async def __aenter__(self) -> '_AsyncLockWrapper':
        await self._lock.__aenter__()
        # Simulate another coroutine setting cache while we have the lock
        if self._first_acquire:
            self._first_acquire = False
            _access_private_cache(self._awaitable, self._cache_value)
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._lock.__aexit__(*args)


class _MockTrioLock:
    """Mock trio lock for testing."""

    def __init__(self) -> None:
        self._locked = False

    async def __aenter__(self) -> '_MockTrioLock':
        while self._locked:
            await asyncio.sleep(0.001)
        self._locked = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._locked = False


class _MockTrioLockSimple:
    """Simple mock trio lock for testing."""

    def __init__(self) -> None:
        self._locked = False

    async def __aenter__(self) -> '_MockTrioLockSimple':
        self._locked = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._locked = False


async def _simple_counter_coro(counter: CallCounter, return_value: int = 42):
    """Simple coroutine that increments counter and returns value."""
    counter.increment()
    return return_value


async def _simple_coro_for_threading_test(counter: CallCounter):
    """Simple coroutine for threading lock test."""
    counter.increment()
    return 42


async def _simple_coro_for_async_test(counter: CallCounter):
    """Simple coroutine for async lock test."""
    counter.increment()
    return 42


async def _slow_coro_for_race_test(counter: CallCounter):
    """Coroutine that waits for events in race condition test."""
    counter.increment()
    # Wait a bit to ensure other tasks are waiting
    await asyncio.sleep(0.01)
    return 42


async def _task1_for_race_test(
    awaitable: ReAwaitable, cache_set_event: asyncio.Event
) -> int:
    """First task that will set the cache in race condition test."""
    result: int = await awaitable
    cache_set_event.set()  # Signal that cache is set
    return result


async def _task2_for_race_test(
    awaitable: ReAwaitable, lock_acquired_event: asyncio.Event
) -> int:
    """Second task that will find cache already set in race condition test."""
    # Wait a tiny bit to ensure task1 starts first
    await asyncio.sleep(0.001)
    # Now try to access - this should hit the false branch
    result: int = await awaitable
    lock_acquired_event.set()
    return result


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
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that no exceptions were raised
    for result in task_results:
        assert not isinstance(result, Exception)

    # The underlying coroutine should only be called once
    assert counter.count == 1

    # All results should be the same
    assert all(res == 42 for res in task_results)


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

    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check that no exceptions were raised
    for result in task_results:
        assert not isinstance(result, Exception)

    # Check that each awaitable returned its correct value multiple times
    assert task_results[0] == task_results[1] == 0
    assert task_results[2] == task_results[3] == 1
    assert task_results[4] == task_results[5] == 2


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
    # Also need to mock the trio import to fail
    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None}),
    ):
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


async def _repr_test_func() -> int:
    """Test function for repr test."""
    return 1


def test_reawaitable_repr():
    """Test that ReAwaitable repr matches the coroutine repr."""
    coro = _repr_test_func()
    awaitable = ReAwaitable(coro)

    # The repr should delegate to the coroutine's repr
    repr_result = repr(awaitable)
    coro_repr = repr(coro)

    # They should be equal
    assert repr_result == coro_repr
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
    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
        # This should execute the fallback and hit the branch we need
        result: int = await awaitable
        assert result == 42
        assert counter.count == 1

        # Verify we took the fallback path by checking _lock is still None
        assert _access_private_lock(awaitable) is not None


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

    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
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

    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
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


@pytest.mark.asyncio
async def test_trio_framework_support():
    """Test ReAwaitable with trio-style lock."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Create a mock trio module
    mock_trio = types.ModuleType('trio')
    mock_trio.Lock = _MockTrioLock  # type: ignore[attr-defined] # noqa: WPS609

    # Simulate trio environment
    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No asyncio')),
        patch.dict('sys.modules', {'trio': mock_trio}),
    ):
        # Should work with trio-style lock
        result1: int = await awaitable
        result2: int = await awaitable

        assert result1 == result2 == 42
        assert counter.count == 1


@pytest.mark.asyncio
async def test_debug_logging_asyncio_lock(caplog):
    """Test that asyncio lock selection is logged at DEBUG level."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    with caplog.at_level(
        logging.DEBUG, logger='returns.primitives.reawaitable'
    ):
        await awaitable

    # Check that asyncio lock selection was logged
    log_messages = [record.message for record in caplog.records]
    assert any(
        'Using asyncio.Lock for concurrency control' in msg
        for msg in log_messages
    )


@pytest.mark.asyncio
async def test_debug_logging_trio_fallback(caplog):
    """Test that trio fallback is logged at DEBUG level."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    # Create a mock trio module
    mock_trio = types.ModuleType('trio')
    mock_trio.Lock = _MockTrioLockSimple  # type: ignore[attr-defined] # noqa: WPS609

    with (
        caplog.at_level(logging.DEBUG, logger='returns.primitives.reawaitable'),
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': mock_trio}),
    ):
        await awaitable

    # Check that trio lock selection was logged with fallback reason
    log_messages = [record.message for record in caplog.records]
    assert any(
        'asyncio.Lock unavailable' in msg and 'trying trio' in msg
        for msg in log_messages
    )
    assert any(
        'Using trio.Lock for concurrency control' in msg for msg in log_messages
    )


@pytest.mark.asyncio
async def test_debug_logging_threading_fallback(caplog):
    """Test that threading lock fallback is logged at DEBUG level."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    with (
        caplog.at_level(logging.DEBUG, logger='returns.primitives.reawaitable'),
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
        # First await to cache the value
        result1: int = await awaitable
        # Second await should use cached value
        result2: int = await awaitable

    assert result1 == result2 == 42
    assert counter.count == 1  # Only called once

    # Check that all fallback steps were logged
    log_messages = [record.message for record in caplog.records]
    assert any(
        'asyncio.Lock unavailable' in msg and 'trying trio' in msg
        for msg in log_messages
    )
    assert any(
        'trio.Lock unavailable' in msg and 'trying anyio' in msg
        for msg in log_messages
    )
    assert any(
        'anyio.Lock unavailable' in msg
        and 'falling back to threading.Lock' in msg
        for msg in log_messages
    )
    assert any(
        'Using threading.Lock fallback for concurrency control' in msg
        for msg in log_messages
    )


@pytest.mark.asyncio
async def test_async_lock_branch_direct_manipulation():
    """Test async lock branch by direct manipulation of internal state."""
    counter = CallCounter()
    awaitable = ReAwaitable(_simple_counter_coro(counter))

    # First, create the async lock
    await awaitable
    assert counter.count == 1

    # Now we'll manipulate internal state to test the branch
    # Reset cache to sentinel
    _access_private_cache(awaitable, _get_sentinel())

    # Get the lock
    lock = _access_private_lock(awaitable)

    # Manually enter the lock context
    async with lock:
        # Now set the cache while we're inside the lock
        _access_private_cache(awaitable, 999)

        # Call _awaitable directly - this should hit the false branch
        # because cache is no longer sentinel
        result = await _call_private_awaitable(awaitable)

    assert result == 999
    assert counter.count == 1  # Coro should not be called again


@pytest.mark.asyncio
async def test_logging_only_occurs_on_first_await(caplog):
    """Test that lock selection logging only occurs once per instance."""
    counter = CallCounter()
    awaitable = ReAwaitable(_example_coro_with_counter_no_sleep(counter))

    with caplog.at_level(
        logging.DEBUG, logger='returns.primitives.reawaitable'
    ):
        # Multiple awaits on same instance
        await awaitable
        await awaitable
        await awaitable

    # Should only see lock creation logs once
    lock_creation_messages = [
        record.message
        for record in caplog.records
        if 'Using asyncio.Lock for concurrency control' in record.message
    ]
    assert len(lock_creation_messages) == 1


async def _setup_threading_lock_test(counter: CallCounter):
    """Set up ReAwaitable with threading lock for testing."""
    awaitable = ReAwaitable(_simple_coro_for_threading_test(counter))

    # Force threading lock by making asyncio.Lock unavailable
    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
        # First, create the lock
        await awaitable  # This creates the lock and sets cache

        # Reset cache to simulate concurrent access
        _access_private_cache(awaitable, _get_sentinel())

        # Get original lock and wrap it
        original_lock = _access_private_lock(awaitable)
        wrapped_lock = _ThreadingLockWrapper(original_lock, awaitable, 99)
        _access_private_lock(awaitable, wrapped_lock)

        return awaitable


@pytest.mark.asyncio
async def test_threading_lock_cached_branch():
    """Test threading lock path where cache is set while waiting for lock."""
    counter = CallCounter()

    # Force threading lock by making asyncio.Lock unavailable
    with (
        patch('asyncio.Lock', side_effect=RuntimeError('No event loop')),
        patch.dict('sys.modules', {'trio': None, 'anyio': None}),
    ):
        awaitable = await _setup_threading_lock_test(counter)
        assert counter.count == 1

        # Now await again - this should hit the branch where cache is set
        result = await awaitable
        assert result == 99  # Should get the value set by our wrapper
        assert counter.count == 1  # Coroutine should not be called again


@pytest.mark.asyncio
async def test_async_lock_cached_branch():
    """Test async lock path where cache is set while waiting for lock."""
    counter = CallCounter()

    awaitable = ReAwaitable(_simple_coro_for_async_test(counter))
    # First await to create the lock
    await awaitable
    assert counter.count == 1

    # Reset cache to sentinel to force re-evaluation
    _access_private_cache(awaitable, _get_sentinel())

    # Get the original async lock
    original_lock = _access_private_lock(awaitable)

    # Replace the lock with our wrapper
    _access_private_lock(
        awaitable, _AsyncLockWrapper(original_lock, awaitable, 99)
    )

    # Call _awaitable directly to ensure we go through the lock path
    # This should hit the branch where cache is already set inside the lock
    result = await _call_private_awaitable(awaitable)
    assert result == 99  # Should get the value set by our wrapper
    assert counter.count == 1  # Coroutine should not be called again


@pytest.mark.asyncio
async def test_async_lock_false_branch_concurrent_race():
    """Test the exact async lock false branch with real concurrent access."""
    counter = CallCounter()
    cache_set_event = asyncio.Event()
    lock_acquired_event = asyncio.Event()

    awaitable = ReAwaitable(_slow_coro_for_race_test(counter))

    # Run both tasks concurrently
    concurrent_results = await asyncio.gather(
        _task1_for_race_test(awaitable, cache_set_event),
        _task2_for_race_test(awaitable, lock_acquired_event),
    )

    # Both should get the same result
    assert concurrent_results[0] == concurrent_results[1] == 42
    # Coroutine should only be called once
    assert counter.count == 1
    # Both events should be set
    assert cache_set_event.is_set()
    assert lock_acquired_event.is_set()
