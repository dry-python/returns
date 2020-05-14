from typing import TypeVar, overload

from returns.io import IOResult
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


@overload
def _swap(
    container: Result[_ValueType, _ErrorType],
) -> Result[_ErrorType, _ValueType]:
    """Case for Result."""


@overload
def _swap(
    container: IOResult[_ValueType, _ErrorType],
) -> IOResult[_ErrorType, _ValueType]:
    """Case for IOResult."""


def _swap(container):
    """
    Swaps value and error types in a container.

    Why? Because we have a lot of ``.bind`` related helpers
    and none ``.rescue`` related helpers.

    So, you can ``swap`` a container to handle errors in a simple way,
    and then swap it back to continue normal execution.

    .. code:: python

      >>> from returns.converters import swap
      >>> from returns.io import IOResult, IOSuccess, IOFailure

      >>> container: IOResult[int, str] = IOSuccess(1)
      >>> swapped: IOResult[str, int] = swap(container)
      >>> assert swapped == IOFailure(1)

      >>> container: IOResult[int, str] = IOFailure('error')
      >>> assert swap(container) == IOSuccess('error')

    And here's how you can handle errors easily:

    .. code:: python

      >>> from returns.converters import swap
      >>> from returns.io import IOResult, IOSuccess
      >>> from returns.result import Result, Success

      >>> def function(error: str) -> Result[str, int]:
      ...     return Success('Very bad error: ' + error)
      ...

      >>> container: IOResult[int, str] = IOFailure('boom')
      >>> # You can `.rescue_result`, but you can `.bind_result` instead!
      >>> assert swap(
      ...     swap(container).bind_result(function),
      ... ) == IOFailure('Very bad error: boom')

    This converter supports only containers
    that have ``.success_type`` property.

    Basically ``Result`` and ``IOResult``.

    """
    if isinstance(container, container.success_type):
        return container.bind(lambda inner: container.from_failure(inner))
    return container.rescue(lambda inner: container.from_value(inner))
