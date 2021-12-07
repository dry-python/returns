import pytest

from returns.context import (
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.contrib.pytest import ReturnsAsserts
from returns.functions import identity
from returns.future import FutureResult
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success


def _under_test(
    container,
    *,
    should_lash: bool = False,
):
    if should_lash:
        return container.lash(lambda inner: container.from_failure(inner))
    return container.bind(lambda inner: container.from_value(inner))


@pytest.mark.parametrize('container', [
    Success(1),
    Failure(1),
    IOSuccess(1),
    IOFailure(1),
    RequiresContextIOResult.from_value(1),
    RequiresContextIOResult.from_failure(1),
    RequiresContextFutureResult.from_value(1),
    RequiresContextFutureResult.from_failure(1),
    RequiresContextResult.from_value(1),
    RequiresContextResult.from_failure(1),
    FutureResult.from_value(1),
    FutureResult.from_failure(1),
])
@pytest.mark.parametrize('kwargs', [
    {'should_lash': True},
])
def test_error_handled(returns: ReturnsAsserts, container, kwargs):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    assert not returns._errors_handled  # noqa: WPS437
    error_handled = _under_test(container, **kwargs)

    assert returns.is_error_handled(error_handled)
    assert returns.is_error_handled(error_handled.map(identity))
    assert returns.is_error_handled(error_handled.alt(identity))

    assert returns._errors_handled  # noqa: WPS437


@pytest.mark.parametrize('container', [
    Success(1),
    Failure(1),
    IOSuccess(1),
    IOFailure(1),
    RequiresContextIOResult.from_value(1),
    RequiresContextIOResult.from_failure(1),
    RequiresContextFutureResult.from_value(1),
    RequiresContextFutureResult.from_failure(1),
    RequiresContextResult.from_value(1),
    RequiresContextResult.from_failure(1),
])
def test_error_not_handled(returns: ReturnsAsserts, container):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    assert not returns._errors_handled  # noqa: WPS437
    error_handled = _under_test(container)

    assert not returns.is_error_handled(container)
    assert not returns.is_error_handled(error_handled)
    assert not returns.is_error_handled(error_handled.map(identity))
    assert not returns.is_error_handled(error_handled.alt(identity))

    assert not returns._errors_handled  # noqa: WPS437


@pytest.mark.anyio()
@pytest.mark.parametrize('container', [
    FutureResult.from_value(1),
    FutureResult.from_failure(1),
    RequiresContextFutureResult.from_value(1),
    RequiresContextFutureResult.from_failure(1),
])
async def test_error_not_handled_async(returns: ReturnsAsserts, container):
    """Demo on how to use ``pytest`` helpers to work with error handling."""
    error_handled = _under_test(container)

    assert not returns.is_error_handled(container)
    assert not returns.is_error_handled(error_handled)
    assert not returns.is_error_handled(error_handled.map(identity))
    assert not returns.is_error_handled(error_handled.alt(identity))
