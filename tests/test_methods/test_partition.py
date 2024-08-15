
import pytest

from returns.io import IO, IOResult
from returns.maybe import Nothing, Some
from returns.methods import partition
from returns.result import Failure, Success


@pytest.mark.parametrize(('containers', 'expected'), [
    (
        (Success(1), Success(2), Failure(None), Success(3)),
        ([1, 2, 3], [None]),
    ),
    (
        (
            IOResult.from_value(1),
            IOResult.from_failure(2),
            IOResult.from_value(3),
            IOResult.from_failure(4),
        ),
        ([IO(1), IO(3)], [IO(2), IO(4)]),
    ),
    (
        (Some(1), Some(2), Nothing),
        ([1, 2], [None]),
    ),
    ((), ([], [])),
])
def test_partition(containers, expected):
    """Test partition function."""
    assert partition(containers) == expected
