from typing import Callable, TypeVar

from returns.interfaces.applicative import ApplicativeN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ApplicativeKind = TypeVar('_ApplicativeKind', bound=ApplicativeN)


def internal_apply(
    container: KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
    other: KindN[
        _ApplicativeKind,
        Callable[[_FirstType], _UpdatedType],
        _SecondType,
        _ThirdType,
    ],
) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Calls a wrapped function in a container on the first container.

    It is not marked as ``@kinded``, because this function is intended
    to be used inside a kinded context:
    like in :func:`returns.pointfree.apply.apply`.
    It returns ``KindN[]`` instance, not a real type.

    If you wish to use the user-facing ``apply``
    that infers the return type correctly,
    use :func:`~bind` function instead.

    .. code:: python

      >>> from returns.methods import apply
      >>> from returns.maybe import Some, Nothing

      >>> def example(argument: int) -> int:
      ...     return argument + 1

      >>> assert apply(Some(1), Some(example)) == Some(2)
      >>> assert apply(Nothing, Some(example)) == Nothing

    Note, that this function works for all containers with ``.apply`` method.
    See :class:`returns.primitives.interfaces.Applicative.ApplicativeN`
    for more info.

    """
    return container.apply(other)


#: Kinded version of :func:`~internal_apply`, use it to infer real return type.
apply = kinded(internal_apply)
