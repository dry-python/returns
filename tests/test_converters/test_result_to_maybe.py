import pytest

from returns.converters import result_to_maybe
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize('inner_value', [
    1,
    [],
    '',
])
def test_success_to_some(inner_value):
    """Ensures that `Success` is always converted to `Some`."""
    assert result_to_maybe(Success(inner_value)) == Some(inner_value)


def test_success_to_nothing():
    """Ensures that `Success(None_` is always converted to `Nothing`."""
    assert result_to_maybe(Success(None)) == Nothing


@pytest.mark.parametrize('inner_value', [
    Exception,
    0,
    None,
])
def test_failure_to_nothing(inner_value):
    """Ensures that `Failure` is always converted to `Nothing`."""
    assert result_to_maybe(Failure(inner_value)) == Nothing
