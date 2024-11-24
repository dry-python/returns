
from typing import Awaitable, Iterable

import anyio

from returns.future import FutureResult
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
      >>> assert anyio.run(gather, [coro()]) == (IOSuccess(1), )
      >>> container = FutureResult(coro())
      >>> assert anyio.run(gather, [container.awaitable]) == (IOSuccess(1), )

    """
    async with anyio.create_task_group() as tg:
        containers_t = tuple(containers)
        ioresults: dict[int, IOResult] = {}

        async def _coro_wrapper(coro: Awaitable):  # noqa: WPS430
            try:
                return IOResult.from_value(await coro)
            except Exception as exc:
                return IOResult.from_failure(exc)

        async def _run_task(coro: Awaitable, index: int):  # noqa: WPS430
            ioresults[index] = await _coro_wrapper(coro)

        for coro_index, coro in enumerate(containers_t):
            tg.start_soon(_run_task, coro, coro_index)
    return tuple([ioresults[key] for key in sorted(ioresults.keys())])
