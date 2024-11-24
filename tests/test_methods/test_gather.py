
import pytest

from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.methods import gather


@pytest.mark.parametrize(('containers', 'expected'), [
    (
        (
            Future.from_value(1),
            FutureResult.from_value(2),
            FutureResult.from_failure(None),
        ),
        (IO(1), IOResult.from_value(2), FutureResult.from_failure(None)),
    ),
    ((), ()),
])
def test_gather(containers, expected):
    """Test partition function."""
    assert gather(containers) == expected
