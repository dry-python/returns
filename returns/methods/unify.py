from typing import Callable, TypeVar, Union

from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.hkt import Kind2, kinded

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_NewErrorType = TypeVar('_NewErrorType')

_ResultLikeKind = TypeVar('_ResultLikeKind', bound=ResultLikeN)


def internal_unify(
    container: Kind2[_ResultLikeKind, _ValueType, _ErrorType],
    function: Callable[
        [_ValueType], Kind2[_ResultLikeKind, _NewValueType, _NewErrorType],
    ],
) -> Kind2[_ResultLikeKind, _NewValueType, Union[_ErrorType, _NewErrorType]]:
    """
    Composes successful container with a function that returns a container.

    Similar to :func:`~returns.methods.bind.bind` but has different type.
    It returns ``Result[ValueType, Union[OldErrorType, NewErrorType]]``
    instead of ``Result[ValueType, OldErrorType]``.

    So, it can be more useful in some situations.
    Probably with specific exceptions.

    .. code:: python

      >>> from returns.methods import cond, unify
      >>> from returns.result import Result, Success, Failure

      >>> def bindable(arg: int) -> Result[int, int]:
      ...     return cond(Result, arg % 2 == 0, arg + 1, arg - 1)

      >>> assert unify(Success(2), bindable) == Success(3)
      >>> assert unify(Success(1), bindable) == Failure(0)
      >>> assert unify(Failure(42), bindable) == Failure(42)

    """
    return container.bind(function)  # type: ignore


#: Kinded version of :func:`~internal_unify`, use it to infer real return type.
unify = kinded(internal_unify)
