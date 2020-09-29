from typing import Type, TypeVar

from returns.context import NoDeps
from returns.interfaces.failable import DiverseFailableN
from returns.primitives.hkt import KindN, kinded

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_DiverseFailableKind = TypeVar('_DiverseFailableKind', bound=DiverseFailableN)


def internal_cond(
    container_type: Type[_DiverseFailableKind],
    is_success: bool,
    success_value: _ValueType,
    error_value: _ErrorType,
) -> KindN[_DiverseFailableKind, _ValueType, _ErrorType, NoDeps]:
    """
    Reduce the boilerplate when choosing paths with ``DiverseFailableN``.

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
