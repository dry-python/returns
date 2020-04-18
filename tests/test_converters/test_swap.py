import pytest

from returns.converters import swap
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success


@pytest.mark.parametrize(('container', 'swapped'), [
    (Success({}), Failure({})),
    (IOSuccess(1), IOFailure(1)),

    (Failure({}), Success({})),
    (IOFailure(1), IOSuccess(1)),
])
def test_swap_results(container, swapped):
    """Ensures that `swap` is always returning the correct type."""
    assert swap(container) == swapped


@pytest.mark.parametrize('container', [
    Success({}),
    IOSuccess(1),

    Failure('a'),
    IOFailure(True),
])
def test_swap_twice(container):
    """Ensures that `swap` is always returning the correct type."""
    assert swap(swap(container)) == container
