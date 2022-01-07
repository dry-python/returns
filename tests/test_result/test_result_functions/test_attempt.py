from typing import Union

from returns.result import Failure, Success, attempt


@attempt
def _function(arg: Union[int, str]) -> float:
    assert isinstance(arg, int)
    return arg / arg


def test_attempt_success():
    """Ensures that safe decorator works correctly for Success case."""
    assert _function(1) == Success(1.0)


def test_attempt_failure():
    """Ensures that safe decorator works correctly for Failure case."""
    assert _function('string') == Failure('string')
