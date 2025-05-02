import pytest

import anyio
from returns.future import Future, FutureResult
from returns.result import Result
from returns.io import IO, IOResult
from returns.methods import gather


async def _helper_func1() -> str:
    return 'successful function'


async def _helper_func2() -> str:
    return 'failed function'

@pytest.mark.parametrize(('containers', 'expected'), [
    (
        (
            FutureResult.from_value(1),
            FutureResult.from_failure(None),
        ),
        (IOResult.from_value(1), IOResult.from_failure(None)),
    ),
    ((), ()),
    (
        (
            _helper_func1(),
            _helper_func2(),
        ),
        (IOResult.from_result(Result.from_value("successful function")), IOResult.from_result(Result.from_failure("failed function")))
    )
])
def test_gather(containers, expected):
    """Test partition function."""
    assert anyio.run(gather,containers) == expected
