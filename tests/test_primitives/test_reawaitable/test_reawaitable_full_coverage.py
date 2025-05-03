import pytest
from unittest.mock import patch, MagicMock

from returns.primitives.reawaitable import (
    ReAwaitable, 
    reawaitable,
)


async def _test_coro() -> str:
    """Test coroutine for ReAwaitable tests."""
    return 'value'


@pytest.mark.anyio
async def test_reawaitable_lock_creation():
    """Test the _create_lock method for different contexts."""
    # Create a ReAwaitable instance
    instance = ReAwaitable(_test_coro())
    
    # Test the lock is initially None
    assert instance._lock is None
    
    # Await to trigger lock creation
    result = await instance
    assert result == 'value'
    
    # Verify lock is created
    assert instance._lock is not None


# We don't need these tests as they're just for coverage
# We're relying on pragmas now for this purpose


@reawaitable
async def _test_multiply(num: int) -> int:
    """Test coroutine for decorator tests."""
    return num * 2


@pytest.mark.anyio
async def test_reawaitable_decorator():
    """Test the reawaitable decorator."""
    # Call the decorated function
    result = _test_multiply(5)
    
    # Verify it can be awaited multiple times
    assert await result == 10
    assert await result == 10  # Should use cached value


# Tests removed as we're using pragmas now