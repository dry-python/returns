import pytest

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.converters import flatten
from returns.future import Future, FutureResult
from returns.io import IO, IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize(('container', 'merged'), [
    # Flattens:
    (IO(IO(1)), IO(1)),

    (Success(Success({})), Success({})),
    (IOSuccess(IOSuccess(1)), IOSuccess(1)),

    (Some(Some(None)), Nothing),
    (Some(Some([])), Some([])),

    # Nope:
    (Failure(Failure('a')), Failure(Failure('a'))),
    (Failure(Success('a')), Failure(Success('a'))),
    (IOFailure(IOFailure('a')), IOFailure(IOFailure('a'))),
    (IOFailure(IOSuccess('a')), IOFailure(IOSuccess('a'))),
])
def test_flatten(container, merged):
    """Ensures that `flatten` is always returning the correct type."""
    assert flatten(container) == merged


@pytest.mark.parametrize(('container', 'merged'), [
    (
        RequiresContextResult.from_value(
            RequiresContextResult.from_value(1),
        ),

        RequiresContextResult.from_value(1),
    ),

    (
        RequiresContextIOResult.from_value(
            RequiresContextIOResult.from_value(1),
        ),

        RequiresContextIOResult.from_value(1),
    ),

    (
        RequiresContext.from_value(RequiresContext.from_value(1)),
        RequiresContext.from_value(1),
    ),
])
def test_flatten_context(container, merged):
    """Ensures that `flatten` is always returning the correct type."""
    assert flatten(container)(...) == merged(...)


@pytest.mark.anyio
async def test_flatten_future(subtests):
    """Ensures that `flatten` is always returning the correct type."""
    futures = [
        # Flattens:
        (Future.from_value(Future.from_value(1)), Future.from_value(1)),
        (
            FutureResult.from_value(FutureResult.from_value(1)),
            FutureResult.from_value(1),
        ),
    ]

    for container, merged in futures:
        with subtests.test(container=container, merged=merged):
            assert await flatten(container) == await merged  # type: ignore


@pytest.mark.anyio
async def test_non_flatten_future(subtests):
    """Ensures that `flatten` is always returning the correct type."""
    futures = [
        # Not flattens:
        FutureResult.from_failure(FutureResult.from_failure(1)),
    ]

    for cont in futures:
        with subtests.test(container=cont):
            assert isinstance(
                (await flatten(cont)).failure()._inner_value,  # noqa: WPS437
                FutureResult,
            )
