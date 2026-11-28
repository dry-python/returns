from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, overload

from returns._internal.pipeline.flow import flow as flow
from returns._internal.pipeline.managed import managed as managed
from returns._internal.pipeline.pipe import pipe as pipe
from returns.interfaces.unwrappable import Unwrappable
from returns.primitives.exceptions import UnwrapFailedError

if TYPE_CHECKING:
    from typing_extensions import TypeIs

    from returns.io import IOResult, IOSuccess
    from returns.maybe import Maybe, Some
    from returns.result import Result, Success

_ValueType = TypeVar('_ValueType')


@overload
def is_successful(
    container: Result[_ValueType, Any],
) -> TypeIs[Success[_ValueType]]: ...


@overload
def is_successful(
    container: Maybe[_ValueType],
) -> TypeIs[Some[_ValueType]]: ...


@overload
def is_successful(
    container: IOResult[_ValueType, Any],
) -> TypeIs[IOSuccess[_ValueType]]: ...


@overload
def is_successful(container: Unwrappable[Any, Any]) -> bool: ...


def is_successful(container: Unwrappable[Any, Any]) -> bool:
    """
    Determines if a container was successful or not.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> from returns.io import IOSuccess, IOFailure

      >>> assert is_successful(Some(1))
      >>> assert not is_successful(Nothing)

      >>> assert is_successful(Success(1))
      >>> assert not is_successful(Failure(1))

      >>> assert is_successful(IOSuccess(1))
      >>> assert not is_successful(IOFailure(1))

    This function can work with containers
    that are instance of :class:`returns.interfaces.unwrappable.Unwrappable`.

    .. rubric:: Type narrowing

    For ``Result``, ``Maybe`` and ``IOResult`` this function is typed
    with :class:`typing_extensions.TypeIs`,
    so the successful branch narrows the container
    to its successful type: :class:`~returns.result.Success`,
    :class:`~returns.maybe.Some` or :class:`~returns.io.IOSuccess`:

    .. code:: python

      >>> from returns.result import Result

      >>> def get_number(container: Result[int, str]) -> int:
      ...     if is_successful(container):
      ...         return container.unwrap()
      ...     return 0

      >>> assert get_number(Success(1)) == 1
      >>> assert get_number(Failure('a')) == 0

    Other ``Unwrappable`` containers still return a plain ``bool``.

    """
    try:
        container.unwrap()
    except UnwrapFailedError:
        return False
    return True
