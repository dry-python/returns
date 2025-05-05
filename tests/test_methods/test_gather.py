import anyio
import pytest

from returns.future import FutureResult
from returns.io import IOResult
from returns.methods import gather
from returns.result import Result


async def _helper_func1() -> str:
    return 'successful function'


async def _helper_func2() -> str:
    return 'failed function'


@pytest.mark.parametrize(
    ('containers', 'expected'),
    [
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
            (
                IOResult.from_result(Result.from_value('successful function')),
                IOResult.from_result(Result.from_failure('failed function')),
            ),
        ),
    ],
)
def test_gather(containers, expected):
    """Test partition function."""
    assert anyio.run(gather, containers) == expected
