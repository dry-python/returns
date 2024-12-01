
import pytest

from returns.result import Success, safe


@safe
def _function(number: int) -> float:
    return number / number


@safe(exceptions=(ZeroDivisionError,))
def _function_two(number: int | str) -> float:
    assert isinstance(number, int)
    return number / number


@safe((ZeroDivisionError,))  # no name
def _function_three(number: int | str) -> float:
    assert isinstance(number, int)
    return number / number


def test_safe_success():
    """Ensures that safe decorator works correctly for Success case."""
    assert _function(1) == Success(1.0)


def test_safe_failure():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = _function(0)
    assert isinstance(failed.failure(), ZeroDivisionError)


def test_safe_failure_with_expected_error():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = _function_two(0)
    assert isinstance(failed.failure(), ZeroDivisionError)

    failed2 = _function_three(0)
    assert isinstance(failed2.failure(), ZeroDivisionError)


def test_safe_failure_with_non_expected_error():
    """Ensures that safe decorator works correctly for Failure case."""
    with pytest.raises(AssertionError):
        _function_two('0')
