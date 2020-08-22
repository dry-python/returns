from typing import Callable, TypeVar

from returns.interfaces.specific.ioresult import IOResultLikeN
from returns.methods.compose_result import internal_compose_result
from returns.primitives.hkt import Kind3, Kinded, kinded
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_ThirdType = TypeVar('_ThirdType')

_IOResultLikeKind = TypeVar('_IOResultLikeKind', bound=IOResultLikeN)


def compose_result(
    function: Callable[
        [Result[_ValueType, _ErrorType]],  # noqa: DAR101, DAR201
        Kind3[_IOResultLikeKind, _NewValueType, _ErrorType, _ThirdType],
    ],
) -> Kinded[Callable[
    [Kind3[_IOResultLikeKind, _ValueType, _ErrorType, _ThirdType]],
    Kind3[_IOResultLikeKind, _NewValueType, _ErrorType, _ThirdType],
]]:
    """
    Composes inner ``Result`` with ``IOResultLike`` returning function.

    Can be useful when you need an access to both states of the result.

    .. code:: python

      >>> from returns.io import IOResult, IOSuccess, IOFailure
      >>> from returns.pointfree import compose_result
      >>> from returns.result import Result

      >>> def modify_string(container: Result[str, str]) -> IOResult[str, str]:
      ...     return IOResult.from_result(
      ...         container.map(str.upper).alt(str.lower),
      ...     )

      >>> assert compose_result(modify_string)(IOSuccess('success')) == IOSuccess('SUCCESS')
      >>> assert compose_result(modify_string)(IOFailure('FAILURE')) == IOFailure('failure')

      # doctest: # noqa: E501

    """
    @kinded
    def factory(
        container: Kind3[_IOResultLikeKind, _ValueType, _ErrorType, _ThirdType],
    ) -> Kind3[_IOResultLikeKind, _NewValueType, _ErrorType, _ThirdType]:
        return internal_compose_result(container, function)
    return factory
