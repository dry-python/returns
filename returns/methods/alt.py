from typing import Callable, TypeVar

from returns.interfaces.altable import AltableN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_AltableKind = TypeVar('_AltableKind', bound=AltableN)


def internal_alt(
    container: KindN[_AltableKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_SecondType], _UpdatedType],
) -> KindN[_AltableKind, _FirstType, _UpdatedType, _ThirdType]:
    """
    Maps a function over a container.

    .. code:: python

      >>> from returns.methods.alt import alt
      >>> from returns.result import Failure, Success

      >>> def example(argument: int) -> int:
      ...     return argument + 1

      >>> assert alt(Success(1), example) == Success(1)
      >>> assert alt(Failure(1), example) == Failure(2)

    Note, that this function works for all containers with ``.alt`` method.
    See :class:`returns.primitives.interfaces.altable.AltableN` for more info.

    """
    return container.alt(function)


#: Kinded version of :func:`~internal_alt`, use it to infer real return type.
alt = kinded(internal_alt)
