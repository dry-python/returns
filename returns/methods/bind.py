from typing import Callable, TypeVar

from returns.interfaces.bindable import BindableN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_BindableKind = TypeVar('_BindableKind', bound=BindableN)


def internal_bind(
    container: KindN[_BindableKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[
        [_FirstType],
        KindN[_BindableKind, _UpdatedType, _SecondType, _ThirdType],
    ],
) -> KindN[_BindableKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a function over a container.

    .. code:: python

      >>> from returns.methods import bind
      >>> from returns.maybe import Maybe, Some, Nothing

      >>> def example(argument: int) -> Maybe[int]:
      ...     return Some(argument + 1)

      >>> assert bind(Some(1), example) == Some(2)
      >>> assert bind(Nothing, example) == Nothing

    Note, that this function works for all containers with ``.bind`` method.
    See :class:`returns.primitives.interfaces.bindable.BindableN` for more info.

    """
    return container.bind(function)


#: Kinded version of :func:`~internal_bind`, use it to infer real return type.
bind = kinded(internal_bind)
