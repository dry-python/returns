
from returns.io import IOSuccess, impure_safe


@impure_safe
def _function(number: int) -> float:
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
