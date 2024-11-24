# flake8: noqa: WPS102

from typing import Awaitable, Iterable

import anyio

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
      >>> from returns.methods import gather
      >>> from returns.io import IOSuccess

      >>> async def coro():
      ...    return 1
      >>> assert anyio.run(gather, [coro()]) == (IOSuccess(1), )
    """
    async with anyio.create_task_group() as tg:
        ioresults: dict[int, IOResult] = {}

        async def _run_task(coro: Awaitable, index: int):  # noqa: WPS430
            ioresult: IOResult
            try:
                ioresult = IOResult.from_value(await coro)
            except Exception as exc:
                ioresult = IOResult.from_failure(exc)
            ioresults[index] = ioresult

        for coro_index, coro in enumerate(containers):
            tg.start_soon(_run_task, coro, coro_index)
    return tuple(ioresults[key] for key in sorted(ioresults.keys()))
