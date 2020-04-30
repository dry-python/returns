import pytest

from returns.future import Future, FutureResult
from returns.io import IO


@pytest.mark.anyio
async def test_inner_value(subtests):
    """Ensure that coroutine correct value is preserved for all units."""
    containers = [
        # We have to define these values inside the test, because
        # otherwise `anyio` will `await` reused coroutines.
        # And they have to be fresh. That's why we use subtests for it.
        Future.from_futureresult(FutureResult.from_success(1)),
        Future.from_futureresult(FutureResult.from_failure(1)),
    ]
    for container in containers:
        with subtests.test(container=container):
            assert isinstance(await container, IO)
