import pytest

from returns.context import RequiresContextIOResult, RequiresContextResult
from returns.functions import identity
from returns.future import FutureResult
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success


def _under_test(
    container,
    *,
    should_rescue: bool = False,
    should_fix: bool = False,
):
    if should_rescue:
        return container.rescue(lambda inner: container.from_failure(inner))
    if should_fix:
        return container.fix(identity)
    return container.bind(lambda inner: container.from_value(inner))


@pytest.mark.parametrize('container', [
    Success(1),
    Failure(1),
    IOSuccess(1),
    IOFailure(1),
    RequiresContextIOResult.from_value(1),
    RequiresContextIOResult.from_failure(1),
    RequiresContextResult.from_value(1),
    RequiresContextResult.from_failure(1),
    FutureResult.from_value(1),
    FutureResult.from_failure(1),
])
@pytest.mark.parametrize('kwargs', [
    {'should_rescue': True},
    {'should_fix': True},
    {'should_rescue': True, 'should_fix': True},
])
def test_error_handled(container, returns, kwargs):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    error_handled = _under_test(container, **kwargs)

    assert returns.is_error_handled(error_handled)
    assert returns.is_error_handled(error_handled.map(identity))
    assert returns.is_error_handled(error_handled.alt(identity))


@pytest.mark.parametrize('container', [
    Success(1),
    Failure(1),
    IOSuccess(1),
    IOFailure(1),
    RequiresContextIOResult.from_value(1),
    RequiresContextIOResult.from_failure(1),
    RequiresContextResult.from_value(1),
    RequiresContextResult.from_failure(1),
])
def test_error_not_handled(container, returns):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    error_handled = _under_test(container)

    assert not returns.is_error_handled(container)
    assert not returns.is_error_handled(error_handled)
    assert not returns.is_error_handled(error_handled.map(identity))
    assert not returns.is_error_handled(error_handled.alt(identity))


@pytest.mark.anyio
@pytest.mark.parametrize('container', [
    FutureResult.from_value(1),
    FutureResult.from_failure(1),
])
async def test_error_not_handled_async(container, returns):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    error_handled = _under_test(container)

    assert not returns.is_error_handled(container)
    assert not returns.is_error_handled(error_handled)
    assert not returns.is_error_handled(error_handled.map(identity))
    assert not returns.is_error_handled(error_handled.alt(identity))
