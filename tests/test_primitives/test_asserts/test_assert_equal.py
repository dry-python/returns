from typing import Sequence

import pytest

from returns.context import (
    Reader,
    ReaderFutureResult,
    ReaderIOResult,
    ReaderResult,
)
from returns.contrib.pytest import ReturnsAsserts
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.primitives.asserts import assert_equal
from returns.primitives.container import BaseContainer
from returns.result import Result

_containers: Sequence[BaseContainer] = (
    Result.from_failure(1),
    Result.from_value(1),

    IO(1),
    IOResult.from_failure(1),
    IOResult.from_value(1),

    Maybe.from_value(1),
    Maybe.from_value(None),
    Maybe.from_optional(None),

    Future.from_value(1),
    FutureResult.from_value(1),
    FutureResult.from_failure(1),

    Reader.from_value(1),
    ReaderResult.from_value(1),
    ReaderResult.from_failure(1),
    ReaderIOResult.from_value(1),
    ReaderIOResult.from_failure(1),
    ReaderFutureResult.from_value(1),
    ReaderFutureResult.from_failure(1),
)


@pytest.mark.parametrize('container', _containers)
def test_assert_equal(container, anyio_backend_name: str):
    """Ensure that containers can be equal."""
    assert_equal(container, container, backend=anyio_backend_name)


@pytest.mark.parametrize('container', _containers)
def test_assert_equal_plugin(
    container,
    anyio_backend_name: str,
    returns: ReturnsAsserts,
):
    """Ensure that containers can be equal."""
    returns.assert_equal(container, container, backend=anyio_backend_name)


@pytest.mark.parametrize('container', _containers)
def test_assert_equal_not(container, anyio_backend_name: str):
    """Ensure that containers can be not equal."""
    with pytest.raises(AssertionError):
        assert_equal(
            container,
            container.from_value(2),
            backend=anyio_backend_name,
        )


@pytest.mark.parametrize('container', _containers)
def test_assert_equal_not_plugin(
    container,
    anyio_backend_name: str,
    returns: ReturnsAsserts,
):
    """Ensure that containers can be not equal."""
    with pytest.raises(AssertionError):
        returns.assert_equal(
            container,
            container.from_value(2),
            backend=anyio_backend_name,
        )
