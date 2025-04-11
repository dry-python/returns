import anyio
import pytest

from returns.primitives.reawaitable import ReAwaitable, reawaitable


async def sample_coro():
    await anyio.sleep(0.1)
    return 'done'


@pytest.mark.anyio
async def test_concurrent_awaitable():
    test_target = ReAwaitable(sample_coro())

    async def await_reawaitable():
        return await test_target
    async with anyio.create_task_group() as tg:
        task1 = tg.start_soon(await_reawaitable)
        task2 = tg.start_soon(await_reawaitable)


@pytest.mark.anyio
async def test_reawaitable_decorator():
    """Test the reawaitable decorator with concurrent awaits."""

    @reawaitable
    async def decorated_coro():
        await anyio.sleep(0.1)
        return "decorated"

    instance = decorated_coro()

    # Test multiple awaits
    result1 = await instance
    result2 = await instance

    assert result1 == "decorated"
    assert result1 == result2

    # Test concurrent awaits
    async def await_decorated():
        return await instance

    async with anyio.create_task_group() as tg:
        task1 = tg.start_soon(await_decorated)
        task2 = tg.start_soon(await_decorated)


@pytest.mark.anyio
async def test_reawaitable_repr():
    """Test the __repr__ method of ReAwaitable."""
    
    async def test_func():
        return 1
    
    coro = test_func()
    reawaitable = ReAwaitable(coro)
    
    # Test the representation
    assert repr(reawaitable) == repr(coro)
    
    # Ensure the coroutine is properly awaited
    await reawaitable
