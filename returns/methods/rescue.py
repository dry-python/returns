from typing import Callable, TypeVar

from returns.interfaces.rescuable import RescuableN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_RescuableKind = TypeVar('_RescuableKind', bound=RescuableN)


@kinded
def rescue(
    container: KindN[_RescuableKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[
        [_SecondType],
        KindN[_RescuableKind, _FirstType, _UpdatedType, _ThirdType],
    ],
) -> KindN[_RescuableKind, _FirstType, _UpdatedType, _ThirdType]:
    """
    Bind a function over a container. Works for the second type argument.

    .. code:: python

      >>> from returns.methods.rescue import rescue
      >>> from returns.result import Result, Success, Failure

      >>> def example(argument: int) -> Result[str, int]:
      ...     return Failure(argument + 1)

      >>> assert rescue(Failure(1), example) == Failure(2)
      >>> assert rescue(Success('a'), example) == Success('a')

    Note, that this function works for all containers with ``.rescue`` method.
    See :class:`returns.primitives.interfaces.rescuable.RescuableN`
    for more info.

    """
    return container.rescue(function)
