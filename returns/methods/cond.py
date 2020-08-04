from typing import Type, TypeVar

from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.hkt import Kind2, kinded

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_ResultKind = TypeVar('_ResultKind', bound=ResultLikeN)


def internal_cond(
    container_type: Type[_ResultKind],
    is_success: bool,
    success_value: _ValueType,
    error_value: _ErrorType,
) -> Kind2[_ResultKind, _ValueType, _ErrorType]:
    """
    Help us to reduce the boilerplate when choosing paths with ``ResultLikeN``.

    .. code:: python

      >>> from returns.methods import cond
      >>> from returns.result import Failure, Result, Success

      >>> def is_numeric(string: str) -> Result[str, str]:
      ...     return cond(
      ...         Result,
      ...         string.isnumeric(),
      ...         'It is a number',
      ...         'It is not a number',
      ...     )

      >>> assert is_numeric('42') == Success('It is a number')
      >>> assert is_numeric('non numeric') == Failure('It is not a number')

    """
    if is_success:
        return container_type.from_value(success_value)
    return container_type.from_failure(error_value)


#: Kinded version of :func:`~internal_cond`, use it to infer real return type.
cond = kinded(internal_cond)
