from typing import Callable, Optional, Type, TypeVar, Union, overload

from returns.context import NoDeps
from returns.interfaces.failable import DiverseFailableN, SingleFailableN
from returns.methods.cond import internal_cond
from returns.primitives.hkt import Kinded, KindN

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_DiverseFailableKind = TypeVar('_DiverseFailableKind', bound=DiverseFailableN)
_SingleFailableKind = TypeVar('_SingleFailableKind', bound=SingleFailableN)


@overload
def cond(
    container_type: Type[_SingleFailableKind],
    success_value: _ValueType,
) -> Kinded[
    Callable[
        [bool], KindN[_SingleFailableKind, _ValueType, _ErrorType, NoDeps],
    ]
]:
    """Reduce the boilerplate when choosing paths with ``SingleFailableN``."""


@overload
def cond(
    container_type: Type[_DiverseFailableKind],
    success_value: _ValueType,
    error_value: _ErrorType,
) -> Kinded[
    Callable[
        [bool], KindN[_DiverseFailableKind, _ValueType, _ErrorType, NoDeps],
    ]
]:
    """Reduce the boilerplate when choosing paths with ``DiverseFailableN``."""


def cond(
    container_type: Union[
        Type[_SingleFailableKind], Type[_DiverseFailableKind],
    ],
    success_value: _ValueType,
    error_value: Optional[_ErrorType] = None,
):
    """
    Reduce the boilerplate when choosing paths.

    Works with ``SingleFailableN`` (e.g. ``Maybe``)
    and ``DiverseFailableN`` (e.g. ``Result``).

    Example using ``cond`` with the ``Result`` container:

    .. code:: python

      >>> from returns.pointfree import cond
      >>> from returns.result import Failure, Result, Success

      >>> assert cond(Result, 'success', 'failure')(True) == Success('success')
      >>> assert cond(Result, 'success', 'failure')(False) == Failure('failure')

    Example using ``cond`` with the ``Maybe`` container:

    .. code:: python

      >>> from returns.maybe import Maybe, Some, Nothing

      >>> assert cond(Maybe, 10.0)(True) == Some(10.0)
      >>> assert cond(Maybe, 10.0)(False) == Nothing

    """
    def factory(is_success: bool):
        return internal_cond(
            container_type, is_success, success_value, error_value,
        )
    return factory
