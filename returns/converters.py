# -*- coding: utf-8 -*-

from typing import TypeVar, overload

from returns.generated import coalesce
from returns.io import IO
from returns.maybe import Maybe
from returns.result import Failure, Result, Success

# Contianer internals:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Re-export from generated:
coalesce_maybe = coalesce._coalesce_maybe  # noqa: WPS437
coalesce_result = coalesce._coalesce_result  # noqa: WPS437


def result_to_maybe(
    result_container: Result[_ValueType, _ErrorType],
) -> Maybe[_ValueType]:
    """
    Converts ``Result`` container to ``Maybe`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> result_to_maybe(Success(1)) == Some(1)
      True
      >>> result_to_maybe(Failure(1)) == Nothing
      True
      >>> result_to_maybe(Success(None)) == Nothing
      True

    """
    return Maybe.new(result_container.value_or(None))


def maybe_to_result(
    maybe_container: Maybe[_ValueType],
) -> Result[_ValueType, None]:
    """
    Converts ``Maybe`` container to ``Result`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> maybe_to_result(Nothing) == Failure(None)
      True
      >>> maybe_to_result(Some(1)) == Success(1)
      True
      >>> maybe_to_result(Some(None)) == Failure(None)
      True

    """
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
    """
    Joins two nested containers together.

    .. code:: python

      >>> from returns.maybe import Some
      >>> from returns.result import Success
      >>> from returns.io import IO
      >>> join(IO(IO(1))) == IO(1)
      True
      >>> join(Some(Some(1))) == Some(1)
      True
      >>> join(Success(Success(1))) == Success(1)
      True

    """
    return container._inner_value  # noqa: WPS437
