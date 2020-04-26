
from returns.result import Success, safe


@safe
def _function(number: int) -> float:
    return number / number


def test_safe_success():
    """Ensures that safe decorator works correctly for Success case."""
    assert _function(1) == Success(1.0)


def test_safe_failure():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = _function(0)
    assert isinstance(failed.failure(), ZeroDivisionError)
