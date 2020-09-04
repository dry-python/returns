from typing import Callable, Optional, TypeVar

from returns.interfaces.specific.maybe import MaybeLikeN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_MaybeLikeKind = TypeVar('_MaybeLikeKind', bound=MaybeLikeN)


@kinded
def bind_optional(
    container: KindN[_MaybeLikeKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], Optional[_UpdatedType]],
) -> KindN[_MaybeLikeKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Binds a function returing optional value over a container.

    .. code:: python

      >>> from typing import Optional
      >>> from returns.methods import bind_optional
      >>> from returns.maybe import Some, Nothing

      >>> def example(argument: int) -> Optional[int]:
      ...     return argument + 1 if argument > 0 else None

      >>> assert bind_optional(Some(1), example) == Some(2)
      >>> assert bind_optional(Some(0), example) == Nothing
      >>> assert bind_optional(Nothing, example) == Nothing

    Note, that this function works
    for all containers with ``.bind_optional`` method.
    See :class:`returns.primitives.interfaces.specific.maybe._MaybeLikeKind`
    for more info.

    """
    return container.bind_optional(function)
