import pytest

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.converters import flatten
from returns.io import IO, IOFailure, IOSuccess
from returns.maybe import Some
from returns.result import Failure, Success


@pytest.mark.parametrize(('container', 'merged'), [
    # Flattens:
    (IO(IO(1)), IO(1)),

    (Success(Success({})), Success({})),
    (IOSuccess(IOSuccess(1)), IOSuccess(1)),

    (Some(Some(None)), Some(None)),
    (Some(Some([])), Some([])),

    # Nope:
    (Failure(Failure('a')), Failure(Failure('a'))),
    (IOFailure(IOFailure('a')), IOFailure(IOFailure('a'))),
])
def test_flatten(container, merged):
    """Ensures that `flatten` is always returning the correct type."""
    assert flatten(container) == merged


@pytest.mark.parametrize(('container', 'merged'), [
    (
        RequiresContextResult.from_success(
            RequiresContextResult.from_success(1),
        ),

        RequiresContextResult.from_success(1),
    ),

    (
        RequiresContextIOResult.from_success(
            RequiresContextIOResult.from_success(1),
        ),

        RequiresContextIOResult.from_success(1),
    ),

    (
        RequiresContext.from_value(RequiresContext.from_value(1)),
        RequiresContext.from_value(1),
    ),
])
def test_flatten_context(container, merged):
    """Ensures that `flatten` is always returning the correct type."""
    assert flatten(container)(...) == merged(...)
