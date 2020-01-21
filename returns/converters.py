# -*- coding: utf-8 -*-

from typing import TypeVar, overload

from returns._generated import coalesce  # noqa: WPS436
from returns.context import RequiresContext
from returns.functions import identity
from returns.io import IO
from returns.maybe import Maybe
from returns.result import Failure, Result, Success

# Contianer internals:
_EnvType = TypeVar('_EnvType')
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
def flatten(container: IO[IO[_ValueType]]) -> IO[_ValueType]:
    """Case for ``IO`` container."""


@overload
def flatten(container: Maybe[Maybe[_ValueType]]) -> Maybe[_ValueType]:
    """Case for ``Maybe`` container."""


@overload
def flatten(
    container: Result[Result[_ValueType, _ErrorType], _ErrorType],
) -> Result[_ValueType, _ErrorType]:
    """Case for ``Result`` container."""


@overload
def flatten(
    container: RequiresContext[
        _EnvType, RequiresContext[_EnvType, _ValueType],
    ],
) -> RequiresContext[_EnvType, _ValueType]:
    """Case for ``RequiresContext`` container."""


def flatten(container):
    """
    Joins two nested containers together.

    Please, note that it will not join
    two ``Failure`` for ``Result`` case
    or two ``Nothing`` for ``Maybe`` case together.

    .. code:: python

      >>> from returns.maybe import Some
      >>> from returns.result import Failure, Success
      >>> from returns.io import IO
      >>> from returns.context import Context

      >>> flatten(IO(IO(1))) == IO(1)
      True

      >>> flatten(Some(Some(1))) == Some(1)
      True

      >>> flatten(Success(Success(1))) == Success(1)
      True
      >>> flatten(Failure(Failure(1))) == Failure(Failure(1))
      True

      >>> flatten(
      ...     Context.unit(Context.unit(1)),
      ... )(Context.Empty) == 1
      True

    See also:
        https://bit.ly/2sIviUr

    """
    return container.bind(identity)
