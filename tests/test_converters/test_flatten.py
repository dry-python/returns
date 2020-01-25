# -*- coding: utf-8 -*-

import pytest

from returns.context import Context
from returns.converters import flatten
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
    (IOFailure(IOFailure('a')), IOFailure(IOFailure('a'))),
])
def test_flatten(container, merged):
    """Ensures that `join` is always returning the correct type."""
    assert flatten(container) == merged


def test_flatten_context():
    """Ensures that `join` works with Context."""
    assert flatten(
        Context.unit(Context.unit(1)),
    )(Context.Empty) == 1
