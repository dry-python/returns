
import pytest

from returns.result import Failure, Success, partition


@pytest.mark.parametrize(('containers', 'expected'), [
    (
        (Success(1), Success(2), Failure(None)),
        ([1, 2], [None]),
    ),
])
def test_partition(containers, expected):
    """Test partition function."""
    assert partition(containers) == expected
