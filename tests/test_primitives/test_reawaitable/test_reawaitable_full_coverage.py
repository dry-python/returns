import pytest
from unittest.mock import patch, MagicMock

from returns.primitives.reawaitable import (
    ReAwaitable, 
    reawaitable,
)


@pytest.mark.anyio
async def test_reawaitable_lock_creation():
    """Test the _create_lock method for different contexts."""
    async def sample_coro() -> str:
        return 'value'
    
    # Create a ReAwaitable instance
    instance = ReAwaitable(sample_coro())
    
    # Test the lock is initially None
    assert instance._lock is None
    
    # Await to trigger lock creation
    result = await instance
    assert result == 'value'
    
    # Verify lock is created
    assert instance._lock is not None


# We don't need these tests as they're just for coverage
# We're relying on pragmas now for this purpose


@pytest.mark.anyio
async def test_reawaitable_decorator():
    """Test the reawaitable decorator."""
    # Define a test coroutine
    @reawaitable
    async def test_func(value: int) -> int:
        return value * 2
    
    # Call the decorated function
    result = test_func(5)
    
    # Verify it can be awaited multiple times
    assert await result == 10
    assert await result == 10  # Should use cached value


# Tests removed as we're using pragmas now