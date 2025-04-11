import anyio
import pytest

from returns.primitives.reawaitable import ReAwaitable


async def sample_coro():
    await anyio.sleep(0.1)
    return 'done'


@pytest.mark.anyio
async def test_concurrent_awaitable():
    reawaitable = ReAwaitable(sample_coro())

    async def await_reawaitable():
        return await reawaitable

    async with anyio.create_task_group() as tg:
        task1 = tg.start_soon(await_reawaitable)
        task2 = tg.start_soon(await_reawaitable)
