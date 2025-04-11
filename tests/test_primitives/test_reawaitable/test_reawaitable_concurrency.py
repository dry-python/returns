import anyio
import pytest

from returns.primitives.reawaitable import ReAwaitable, reawaitable


async def sample_coro():
    await anyio.sleep(0.1)
    return 'done'


async def await_helper(awaitable_obj):
    """Helper to await objects in tasks."""
    return await awaitable_obj


@pytest.mark.anyio
async def test_concurrent_awaitable():
    """Test that ReAwaitable works with concurrent awaits."""
    test_target = ReAwaitable(sample_coro())

    async with anyio.create_task_group() as tg:
        tg.start_soon(await_helper, test_target)
        tg.start_soon(await_helper, test_target)


async def _test_coro():  # noqa: WPS430
    await anyio.sleep(0.1)
    return "decorated"


@pytest.mark.anyio  # noqa: WPS210
async def test_reawaitable_decorator():
    """Test the reawaitable decorator with concurrent awaits."""
    decorated = reawaitable(_test_coro)
    instance = decorated()

    # Test multiple awaits
    result1 = await instance
    result2 = await instance

    assert result1 == "decorated"
    assert result1 == result2

    # Test concurrent awaits
    async with anyio.create_task_group() as tg:
        tg.start_soon(await_helper, instance)
        tg.start_soon(await_helper, instance)


@pytest.mark.anyio
async def test_reawaitable_repr():
    """Test the __repr__ method of ReAwaitable."""

    async def test_func():  # noqa: WPS430
        return 1

    coro = test_func()
    target = ReAwaitable(coro)

    # Test the representation
    assert repr(target) == repr(coro)
    # Ensure the coroutine is properly awaited
    await target
