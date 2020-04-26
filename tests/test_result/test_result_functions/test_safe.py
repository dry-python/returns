import pytest

from returns.result import Success, safe


@safe
def _function(number: int) -> float:
    return number / number


@safe
async def _coroutine(number: int) -> float:
    return number / number


def test_safe_success():
    """Ensures that safe decorator works correctly for Success case."""
    assert _function(1) == Success(1.0)


def test_safe_failure():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = _function(0)
    assert isinstance(failed.failure(), ZeroDivisionError)


@pytest.mark.anyio
async def test_async_safe_success():
    """Ensures that safe decorator works correctly for Success case."""
    success = await _coroutine(1)
    assert success == Success(1.0)
    assert success.unwrap() == 1.0


@pytest.mark.anyio
async def test_async_safe_failure():
    """Ensures that safe decorator works correctly for Failure case."""
    failed = await _coroutine(0)
    assert isinstance(failed.failure(), ZeroDivisionError)
