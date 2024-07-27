from typing import Union

import pytest

from returns.future import FutureResult, future_safe
from returns.io import IOFailure, IOSuccess


@future_safe
async def _coro(arg: int) -> float:
    return 1 / arg


@future_safe(exceptions=(ZeroDivisionError,))
async def _coro_two(arg: int) -> float:
    return 1 / arg


@future_safe((ZeroDivisionError,))
async def _coro_three(arg: Union[int, str]) -> float:
    assert isinstance(arg, int)
    return 1 / arg


@pytest.mark.anyio
async def test_future_safe_decorator():
    """Ensure that coroutine marked with ``@future_safe``."""
    future_instance = _coro(2)

    assert isinstance(future_instance, FutureResult)
    assert await future_instance == IOSuccess(0.5)


@pytest.mark.anyio
async def test_future_safe_decorator_failure():
    """Ensure that coroutine marked with ``@future_safe``."""
    future_instance = _coro(0)

    assert isinstance(future_instance, FutureResult)
    assert isinstance(await future_instance, IOFailure)


@pytest.mark.anyio
async def test_future_safe_decorator_w_expected_error(subtests):
    """Ensure that coroutine marked with ``@future_safe``."""
    expected = '<IOResult: <Failure: division by zero>>'

    for future_instance in (_coro_two(0), _coro_three(0)):
        with subtests.test(future_instance=future_instance):
            assert isinstance(future_instance, FutureResult)
            inner_result = await future_instance
            assert str(inner_result) == expected


@pytest.mark.anyio
@pytest.mark.xfail(raises=AssertionError)
async def test_future_safe_decorator_w_unexpected_error():
    """Ensure that coroutine marked with ``@future_safe``."""
    await _coro_three('0')
