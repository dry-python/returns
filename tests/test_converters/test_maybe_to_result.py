import pytest

from returns.converters import maybe_to_result
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize('inner_value', [
    1,
    [],
    '',
])
def test_some_to_success(inner_value):
    """Ensures that `Some` is always converted to `Success`."""
    assert maybe_to_result(Some(inner_value)) == Success(inner_value)


def test_nothing_to_failure():
    """Ensure that `Nothing` is always converted to `Failure`."""
    assert maybe_to_result(Nothing) == Failure(None)
