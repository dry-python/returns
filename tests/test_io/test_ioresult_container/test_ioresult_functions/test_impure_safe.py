from typing import Union

import pytest

from returns.io import IOSuccess, impure_safe


@impure_safe
def _function(number: int) -> float:
    return number / number


@impure_safe(exceptions=(ZeroDivisionError,))
def _function_two(number: Union[int, str]) -> float:
    assert isinstance(number, int)
    return number / number


@impure_safe((ZeroDivisionError,))  # no name
def _function_three(number: Union[int, str]) -> float:
    assert isinstance(number, int)
    return number / number


def test_safe_iosuccess():
    """Ensures that safe decorator works correctly for IOSuccess case."""
    assert _function(1) == IOSuccess(1.0)


def test_safe_iofailure():
    """Ensures that safe decorator works correctly for IOFailure case."""
    failed = _function(0)
    assert isinstance(
        failed.failure()._inner_value, ZeroDivisionError,  # noqa: WPS437
    )


def test_safe_failure_with_expected_error():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = _function_two(0)
    assert isinstance(
        failed.failure()._inner_value,  # noqa: WPS437
        ZeroDivisionError,
    )

    failed2 = _function_three(0)
    assert isinstance(
        failed2.failure()._inner_value,  # noqa: WPS437
        ZeroDivisionError,
    )


def test_safe_failure_with_non_expected_error():
    """Ensures that safe decorator works correctly for Failure case."""
    with pytest.raises(AssertionError):
        _function_two('0')
