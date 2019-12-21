# -*- coding: utf-8 -*-

from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Type, TypeVar, Union, overload

from typing_extensions import Protocol

from returns._generated.pipe import _pipe as pipe  # noqa: F401, WPS436
from returns.maybe import Maybe
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Result

# Logical aliases:
_Unwrapable = Union[Result, Maybe]

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')

# Hacks for functions:
_ReturnResultType = TypeVar(
    '_ReturnResultType',
    bound=Callable[..., Result],
)
_AsyncReturnResultType = TypeVar(
    '_AsyncReturnResultType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, Result]],
)

_ReturnMaybeType = TypeVar(
    '_ReturnMaybeType',
    bound=Callable[..., Maybe],
)
_AsyncReturnMaybeType = TypeVar(
    '_AsyncReturnMaybeType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, Maybe]],
)


def is_successful(container: _Unwrapable) -> bool:
    """
    Determins if a container was successful or not.

    We treat container that raise ``UnwrapFailedError`` on ``.unwrap()``
    not successful.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> is_successful(Some(1))
      True
      >>> is_successful(Nothing)
      False
      >>> is_successful(Success(1))
      True
      >>> is_successful(Failure(1))
      False

    """
    try:
        container.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True


class _PipelineResultProtocol(Protocol):
    @overload
    def __call__(self, function: _ReturnResultType) -> _ReturnResultType:
        """Sync pipeline case for ``Result`` container."""

    @overload  # noqa: F811
    def __call__(
        self, function: _AsyncReturnResultType,
    ) -> _AsyncReturnResultType:
        """Async pipeline case for ``Result`` container."""


class _PipelineMaybeProtocol(Protocol):
    @overload
    def __call__(self, function: _ReturnMaybeType) -> _ReturnMaybeType:
        """Sync pipeline case for ``Maybe`` container."""

    @overload  # noqa: F811
    def __call__(
        self, function: _AsyncReturnMaybeType,
    ) -> _AsyncReturnMaybeType:
        """Async pipeline case for ``Maybe`` container."""


@overload
def pipeline(
    container_type: Type[Result],
) -> _PipelineResultProtocol:
    """Pipeline case for ``Result`` container."""


@overload
def pipeline(
    container_type: Type[Maybe],
) -> _PipelineMaybeProtocol:
    """Pipeline case for ``Maybe`` container."""


def pipeline(container_type):  # noqa: C901, WPS212
    """
    Decorator to enable ``do-notation`` context.

    Should be used for series of computations that rely on ``.unwrap`` method.
    Supports both async and regular functions.

    Works with both ``Maybe`` and ``Result`` containers.

    Example:
    .. code:: python

        >>> from typing import Optional
        >>> @pipeline(Maybe)
        ... def test(one: Optional[int], two: Optional[int]) -> Maybe[int]:
        ...      first = Maybe.new(one).unwrap()
        ...      second = Maybe.new(two).unwrap()
        ...      return Maybe.new(first + second)
        ...
        >>> str(test(1, 2))
        '<Some: 3>'
        >>> str(test(2, None))
        '<Nothing>'

    Make sure to supply the correct container type when creating a pipeline.

    """
    def factory(function):
        if iscoroutinefunction(function):
            async def decorator(*args, **kwargs):  # noqa: WPS430
                try:
                    return await function(*args, **kwargs)
                except UnwrapFailedError as exc:
                    return exc.halted_container
        else:
            def decorator(*args, **kwargs):  # noqa: WPS430
                try:
                    return function(*args, **kwargs)
                except UnwrapFailedError as exc:
                    return exc.halted_container
        return wraps(function)(decorator)
    return factory
