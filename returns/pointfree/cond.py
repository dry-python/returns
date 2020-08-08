from typing import Callable, Type, TypeVar

from returns.interfaces.specific.result import ResultLikeN
from returns.methods.cond import internal_cond
from returns.primitives.hkt import Kind2, Kinded, kinded

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_ResultKind = TypeVar('_ResultKind', bound=ResultLikeN)


def cond(
    container_type: Type[_ResultKind],
    success_value: _ValueType,
    error_value: _ErrorType,
) -> Kinded[Callable[[bool], Kind2[_ResultKind, _ValueType, _ErrorType]]]:
    """
    Help us to reduce the boilerplate when choosing paths with ``ResultLikeN``.

    .. code:: python

      >>> from returns.pointfree import cond
      >>> from returns.result import Failure, Result, Success

      >>> assert cond(Result, 'success', 'failure')(True) == Success('success')
      >>> assert cond(Result, 'success', 'failure')(False) == Failure('failure')

    """
    @kinded
    def factory(
        is_success: bool,
    ) -> Kind2[_ResultKind, _ValueType, _ErrorType]:
        return internal_cond(
            container_type, is_success, success_value, error_value,
        )
    return factory
