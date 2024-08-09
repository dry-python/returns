
import pytest

from returns.future import IOResult
from returns.io import IO
from returns.methods import partition
from returns.result import Failure, Success


@pytest.mark.parametrize(('containers', 'expected'), [
    (
        (Success(1), Success(2), Failure(None)),
        ([1, 2], [None]),
    ),
    (
        (
            IOResult.from_value(1),
            IOResult.from_value(2),
            IOResult.from_failure(None),
        ),
        ([IO(1), IO(2)], [IO(None)]),
    ),
])
def test_partition(containers, expected):
    """Test partition function."""
    assert partition(containers) == expected
