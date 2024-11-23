from typing import Any

from typing import Awaitable, Iterable

import anyio
from returns.future import Future, FutureResult
from returns.io import IOResult



async def gather(
    containers: Iterable[
        Awaitable,
    ],
) -> tuple[IOResult, ...]:
    """
    Execute multiple coroutines concurrently and return their wrapped results.

    .. code:: python

      >>> import anyio
      >>> from returns.methods.gather import gather
      >>> from returns.io import IOSuccess

      >>> async def coro():
      ...    return 1
      >>> assert anyio.run(gather([coro()])) == (IOSuccess(1), )
      >>> container = FutureResult(coro())
      >>> assert anyio.run(gather([container.awaitable])) == (IOSuccess(1), )

    """

    async with anyio.create_task_group() as tg:
        containers_t = tuple(containers)
        results: list[IOResult] = len(containers_t)*[IOResult(None)]

        async def run_task(coro: Awaitable, index: int):
            results[index] = await FutureResult(coro)

        for i, coro in enumerate(containers_t):
            tg.start_soon(run_task, coro, i)
    return tuple(results)

