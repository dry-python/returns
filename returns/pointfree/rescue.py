from typing import Callable, TypeVar

from returns.interfaces.rescuable import RescuableN
from returns.methods.rescue import internal_rescue
from returns.primitives.hkt import Kinded, KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_RescuableKind = TypeVar('_RescuableKind', bound=RescuableN)


def rescue(
    function: Callable[
        [_SecondType],
        KindN[_RescuableKind, _FirstType, _UpdatedType, _ThirdType],
    ],
) -> Kinded[Callable[
    [KindN[_RescuableKind, _FirstType, _SecondType, _ThirdType]],
    KindN[_RescuableKind, _FirstType, _UpdatedType, _ThirdType],
]]:
    """
    Turns function's input parameter from a regular value to a container.

    In other words, it modifies the function
    signature from: ``a -> Container[b]`` to: ``Container[a] -> Container[b]``

    Similar to :func:`returns.pointfree.bind`, but works for failed containers.

    This is how it should be used:

    .. code:: python

      >>> from returns.pointfree import rescue
      >>> from returns.result import Success, Failure, Result

      >>> def example(argument: int) -> Result[str, int]:
      ...     return Success(argument + 1)

      >>> assert rescue(example)(Success('a')) == Success('a')
      >>> assert rescue(example)(Failure(1)) == Success(2)

    Note, that this function works for all containers with ``.rescue`` method.
    See :class:`returns.interfaces.rescuable.Rescuable` for more info.

    """
    @kinded
    def factory(
        container: KindN[_RescuableKind, _FirstType, _SecondType, _ThirdType],
    ) -> KindN[_RescuableKind, _FirstType, _UpdatedType, _ThirdType]:
        return internal_rescue(container, function)
    return factory
