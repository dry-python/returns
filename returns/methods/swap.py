from typing import TypeVar

from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ResultLikeKind = TypeVar('_ResultLikeKind', bound=ResultLikeN)


@kinded
def swap(
    container: KindN[_ResultLikeKind, _FirstType, _SecondType, _ThirdType],
) -> KindN[_ResultLikeKind, _SecondType, _FirstType, _ThirdType]:
    """
    Swaps value and error types in a container.

    Why? Because we have a lot of ``.bind`` related helpers
    and none ``.rescue`` related helpers.

    So, you can ``swap`` a container to handle errors in a simple way,
    and then swap it back to continue normal execution.

    .. code:: python

      >>> from returns.methods import swap
      >>> from returns.io import IOResult, IOSuccess, IOFailure

      >>> container: IOResult[int, str] = IOSuccess(1)
      >>> swapped: IOResult[str, int] = swap(container)
      >>> assert swapped == IOFailure(1)

      >>> container: IOResult[int, str] = IOFailure('error')
      >>> assert swap(container) == IOSuccess('error')

    And here's how you can handle errors easily:

    .. code:: python

      >>> from returns.methods import swap
      >>> from returns.io import IOResult, IOSuccess
      >>> from returns.result import Result, Success

      >>> def function(error: str) -> Result[str, int]:
      ...     return Success('Very bad error: ' + error)

      >>> container: IOResult[int, str] = IOFailure('boom')
      >>> # You cannot `.rescue_result`, but you can `.bind_result` instead!
      >>> assert swap(
      ...     swap(container).bind_result(function),
      ... ) == IOFailure('Very bad error: boom')

    This method supports all ``ResultLikeN`` containers.
    """
    return container.swap()
