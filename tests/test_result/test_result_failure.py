import pytest

from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def test_unwrap_success():
    """Ensures that unwrap works for Success container."""
    with pytest.raises(UnwrapFailedError):
        assert Success(5).failure()


def test_unwrap_failure():
    """Ensures that unwrap works for Failure container."""
    assert Failure(5).failure() == 5
