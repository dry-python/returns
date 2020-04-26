import pytest

from returns.io import IO, IOSuccess, impure_safe


@impure_safe
def _function(number: int) -> float:
    return number / number


@impure_safe
async def _coroutine(number: int) -> float:
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


@pytest.mark.anyio
async def test_async_safe_iosuccess():
    """Ensures that safe decorator works correctly for IOSuccess case."""
    success = await _coroutine(1)
    assert success == IOSuccess(1.0)
    assert success.unwrap() == IO(1.0)


@pytest.mark.anyio
async def test_async_safe_iofailure():
    """Ensures that safe decorator works correctly for IOFailure case."""
    failed = await _coroutine(0)
    assert isinstance(
        failed.failure()._inner_value, ZeroDivisionError,  # noqa: WPS437
    )
