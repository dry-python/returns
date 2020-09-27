from typing import Callable, TypeVar, Union

from returns.interfaces.failable import DiverseFailableN
from returns.primitives.hkt import Kind2, Kinded, kinded

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_NewErrorType = TypeVar('_NewErrorType')

_DiverseFailableKind = TypeVar('_DiverseFailableKind', bound=DiverseFailableN)


def unify(  # noqa: WPS234
    function: Callable[
        [_ValueType], Kind2[_DiverseFailableKind, _NewValueType, _NewErrorType],
    ],
) -> Kinded[
    Callable[
        [Kind2[_DiverseFailableKind, _ValueType, _ErrorType]],
        Kind2[
            _DiverseFailableKind,
            _NewValueType,
            Union[_ErrorType, _NewErrorType],
        ],
    ]
]:
    """
    Composes successful container with a function that returns a container.

    Similar to :func:`~returns.pointfree.bind` but has different type.
    It returns ``Result[ValueType, Union[OldErrorType, NewErrorType]]``
    instead of ``Result[ValueType, OldErrorType]``.

    So, it can be more useful in some situations.
    Probably with specific exceptions.

    .. code:: python

      >>> from returns.methods import cond
      >>> from returns.pointfree import unify
      >>> from returns.result import Result, Success, Failure

      >>> def bindable(arg: int) -> Result[int, int]:
      ...     return cond(Result, arg % 2 == 0, arg + 1, arg - 1)

      >>> assert unify(bindable)(Success(2)) == Success(3)
      >>> assert unify(bindable)(Success(1)) == Failure(0)
      >>> assert unify(bindable)(Failure(42)) == Failure(42)

    """
    @kinded
    def factory(
        container: Kind2[_DiverseFailableKind, _ValueType, _ErrorType],
    ) -> Kind2[
        _DiverseFailableKind, _NewValueType, Union[_ErrorType, _NewErrorType],
    ]:
        return container.bind(function)  # type: ignore
    return factory
