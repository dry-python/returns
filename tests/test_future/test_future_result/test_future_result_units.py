import pytest

from returns.future import Future, FutureResult
from returns.io import IO, IOFailure, IOSuccess
from returns.result import Failure, Success


@pytest.mark.anyio
async def test_inner_value(subtests):
    """Ensure that coroutine correct value is preserved for all units."""
    containers = [
        # We have to define these values inside the test, because
        # otherwise `anyio` will `await` reused coroutines.
        # And they have to be fresh. That's why we use subtests for it.
        FutureResult.from_success(1),
        FutureResult.from_failure(1),

        FutureResult.from_successful_io(IO(1)),
        FutureResult.from_failed_io(IO(1)),

        FutureResult.from_ioresult(IOSuccess(1)),
        FutureResult.from_ioresult(IOFailure(1)),

        FutureResult.from_result(Success(1)),
        FutureResult.from_result(Failure(1)),

        FutureResult.from_successful_future(Future.from_value(1)),
        FutureResult.from_failed_future(Future.from_value(1)),
        FutureResult.from_typecast(Future.from_value(Success(1))),
    ]
    for container in containers:
        with subtests.test(container=container):
            assert (
                await container  # noqa: WPS437
            )._inner_value._inner_value == 1
