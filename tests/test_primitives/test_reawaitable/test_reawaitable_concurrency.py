import anyio
import pytest

from returns.primitives.reawaitable import ReAwaitable, reawaitable


# Fix for issue with multiple awaits on the same ReAwaitable instance:
# https://github.com/dry-python/returns/issues/2108
async def sample_coro() -> str:
    """Sample coroutine that simulates an async operation."""
    await anyio.sleep(
        1
    )  # Increased from 0.1 to reduce chance of random failures
    return 'done'


async def await_helper(awaitable_obj) -> str:
    """Helper to await objects in tasks."""
    return await awaitable_obj


@pytest.mark.anyio
async def test_concurrent_awaitable() -> None:
    """Test that ReAwaitable safely handles concurrent awaits using a lock."""
    test_target = ReAwaitable(sample_coro())

    async with anyio.create_task_group() as tg:
        tg.start_soon(await_helper, test_target)
        tg.start_soon(await_helper, test_target)


@pytest.mark.anyio  # noqa: WPS210
async def test_reawaitable_decorator() -> None:
    """Test the reawaitable decorator with concurrent awaits."""

    async def test_coro() -> str:  # noqa: WPS430
        await anyio.sleep(
            1
        )  # Increased from 0.1 to reduce chance of random failures
        return 'decorated'

    decorated = reawaitable(test_coro)
    instance = decorated()

    # Test multiple awaits
    result1 = await instance
    result2 = await instance

    assert result1 == 'decorated'
    assert result1 == result2

    # Test concurrent awaits
    async with anyio.create_task_group() as tg:
        tg.start_soon(await_helper, instance)
        tg.start_soon(await_helper, instance)


@pytest.mark.anyio
async def test_reawaitable_repr() -> None:
    """Test the __repr__ method of ReAwaitable."""

    async def test_func() -> int:  # noqa: WPS430
        return 1

    coro = test_func()
    target = ReAwaitable(coro)

    # Test the representation
    assert repr(target) == repr(coro)
    # Ensure the coroutine is properly awaited
    await target
