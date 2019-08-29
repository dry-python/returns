# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

from returns.io import IO
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

# Contianer internals:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Aliases:
_FirstType = TypeVar('_FirstType')


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


_coalesce_doc = """
Accepts two functions that handle different cases of containers.

First one handles successful containers like ``Some`` and ``Success``,
and second one for failed containers like ``Nothing`` and ``Failure``.

This function is useful when you need
to coalesce two possible container states into one type.
"""


def _coalesce(success_handler, failure_handler):
    """
    We need this function, because we cannot use a single typed function.

    .. code:: python

      >>> from returns.result import Success, Failure
      >>> f1 = lambda x: x + 1
      >>> f2 = lambda y: y + 'b'
      >>> coalesce_result(f1, f2)(Success(1)) == 2
      True
      >>> coalesce_result(f1, f2)(Failure('a')) == 'ab'
      True

      >>> from returns.maybe import Some, Nothing
      >>> f1 = lambda x: x + 1
      >>> f2 = lambda _: 'a'
      >>> coalesce_maybe(f1, f2)(Some(1)) == 2
      True
      >>> coalesce_maybe(f1, f2)(Nothing) == 'a'
      True

    """
    def decorator(container):
        if is_successful(container):
            return success_handler(container.unwrap())
        return failure_handler(container.failure())
    return decorator


coalesce_result: Callable[
    [
        Callable[[_ValueType], _FirstType],
        Callable[[_ErrorType], _FirstType],
    ],
    Callable[[Result[_ValueType, _ErrorType]], _FirstType],
] = _coalesce
coalesce_result.__doc__ = _coalesce_doc

coalesce_maybe: Callable[
    [
        Callable[[_ValueType], _FirstType],
        Callable[[None], _FirstType],
    ],
    Callable[[Maybe[_ValueType]], _FirstType],
] = _coalesce
coalesce_maybe.__doc__ = _coalesce_doc
