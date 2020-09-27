from typing import Callable, Type, TypeVar

from returns.interfaces.failable import DiverseFailableN
from returns.methods.cond import internal_cond
from returns.primitives.hkt import Kind2, Kinded, kinded

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_DiverseFailableKind = TypeVar('_DiverseFailableKind', bound=DiverseFailableN)


def cond(
    container_type: Type[_DiverseFailableKind],
    success_value: _ValueType,
    error_value: _ErrorType,
) -> Kinded[
    Callable[[bool], Kind2[_DiverseFailableKind, _ValueType, _ErrorType]]
]:
    """
    Reduce the boilerplate when choosing paths with ``DiverseFailableN``.

    .. code:: python

      >>> from returns.pointfree import cond
      >>> from returns.result import Failure, Result, Success

      >>> assert cond(Result, 'success', 'failure')(True) == Success('success')
      >>> assert cond(Result, 'success', 'failure')(False) == Failure('failure')

    """
    @kinded
    def factory(
        is_success: bool,
    ) -> Kind2[_DiverseFailableKind, _ValueType, _ErrorType]:
        return internal_cond(
            container_type, is_success, success_value, error_value,
        )
    return factory
