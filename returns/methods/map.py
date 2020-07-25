from typing import Callable, TypeVar

from returns.interfaces.mappable import MappableN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_MappableKind = TypeVar('_MappableKind', bound=MappableN)


def internal_map(
    container: KindN[_MappableKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], _UpdatedType],
) -> KindN[_MappableKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Maps a function over a container.

    .. code:: python

      >>> from returns.methods.map import internal_map, map_
      >>> from returns.maybe import Some, Nothing

      >>> def example(argument: int) -> int:
      ...     return argument + 1

      >>> bound = map_(Some(1), example)
      >>> assert bound == internal_map(Some(1), example) == Some(2)

      >>> bound = map_(Nothing, example)
      >>> assert bound == internal_map(Nothing, example) == Nothing

    Note, that this function works for all containers with ``.map`` method.
    See :class:`returns.primitives.interfaces.mappable.MappableN` for more info.

    """
    return container.map(function)


#: Kinded version of :func:`~internal_map`, use it to infer real return type.
map_ = kinded(internal_map)
