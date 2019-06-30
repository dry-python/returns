# -*- coding: utf-8 -*-

from typing import TypeVar, overload

from returns.io import IO
from returns.maybe import Maybe
from returns.result import Failure, Result, Success

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


def result_to_maybe(
    result_container: Result[_ValueType, _ErrorType],
) -> Maybe[_ValueType]:
    """Converts ``Result`` container to ``Maybe`` container."""
    return Maybe.new(result_container.value_or(None))


def maybe_to_result(
    maybe_container: Maybe[_ValueType],
) -> Result[_ValueType, None]:
    """Converts ``Maybe`` container to ``Result`` container."""
    inner_value = maybe_container.value_or(None)
    if inner_value is not None:
        return Success(inner_value)
    return Failure(inner_value)


@overload
def join(container: IO[IO[_ValueType]]) -> IO[_ValueType]:
    """Case for ``IO`` container."""


@overload
def join(container: Maybe[Maybe[_ValueType]]) -> Maybe[_ValueType]:
    """Case for ``Maybe`` container."""


@overload
def join(
    container: Result[Result[_ValueType, _ErrorType], _ErrorType],
) -> Result[_ValueType, _ErrorType]:
    """Case for ``Result`` container."""


def join(container):
    """Joins two nested containers together."""
    return container._inner_value  # noqa: Z441
