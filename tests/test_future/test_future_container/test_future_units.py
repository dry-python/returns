from typing import Any, Awaitable, List

import pytest

from returns.future import Future, FutureResult
from returns.io import IO


@pytest.mark.anyio
async def test_inner_value(subtests):
    """Ensure that coroutine correct value is preserved for all units."""
    containers: List[Awaitable[Any]] = [
        # We have to define these values inside the test, because
        # otherwise `anyio` will `await` reused coroutines.
        # And they have to be fresh. That's why we use subtests for it.
        Future.from_value(1),
        Future.from_io(IO(1)),
        Future.from_future_result(FutureResult.from_value(1)),
        Future.from_future_result(FutureResult.from_failure(1)),
    ]
    for container in containers:
        with subtests.test(container=container):
            assert isinstance(await container, IO)
