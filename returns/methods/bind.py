from typing import Callable, TypeVar

from returns.interfaces.bindable import BindableN
from returns.primitives.hkt import KindN, debound, kinded

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

    It is not marked as ``@kinded``, because this function is intended
    to be used inside a kinded context:
    like in :func:`returns.pointfree.bind.bind`.
    It returns ``KindN[]`` instance, not a real type.

    If you wish to use the user-facing ``bind``
    that infers the return type correctly,
    use :func:`~bind` function instead.

    .. code:: python

      >>> from returns.methods.bind import internal_bind, bind
      >>> from returns.maybe import Maybe, Some, Nothing

      >>> def example(argument: int) -> Maybe[int]:
      ...     return Some(argument + 1)

      >>> bound = bind(Some(1), example)
      >>> assert bound == internal_bind(Some(1), example) == Some(2)

      >>> bound = bind(Nothing, example)
      >>> assert bound == internal_bind(Nothing, example) == Nothing

    Note, that this function works for all containers with ``.bind`` method.
    See :class:`returns.primitives.interfaces.BindableN` for more info.

    """
    new_instance, rebound = debound(container)
    return rebound(new_instance.bind(function))


#: Kinded version of :func:`~internal_bind`, use it to infer real return type.
bind = kinded(internal_bind)
