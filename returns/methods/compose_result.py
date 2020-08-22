from typing import Callable, TypeVar

from returns.interfaces.specific.ioresult import IOResultLikeN
from returns.primitives.hkt import Kind3, kinded
from returns.result import Result

_FirstType = TypeVar('_FirstType')
_NewFirstType = TypeVar('_NewFirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_IOResultLikeKind = TypeVar('_IOResultLikeKind', bound=IOResultLikeN)


def internal_compose_result(
    container: Kind3[_IOResultLikeKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[
        [Result[_FirstType, _SecondType]],
        Kind3[_IOResultLikeKind, _NewFirstType, _SecondType, _ThirdType],
    ],
) -> Kind3[_IOResultLikeKind, _NewFirstType, _SecondType, _ThirdType]:
    """
    Composes inner ``Result`` with ``IOResultLike`` returning function.

    Can be useful when you need an access to both states of the result.

    .. code:: python

      >>> from returns.io import IOResult, IOSuccess, IOFailure
      >>> from returns.methods import compose_result
      >>> from returns.result import Result

      >>> def count(container: Result[int, int]) -> IOResult[int, int]:
      ...     return IOResult.from_result(
      ...         container.map(lambda x: x + 1).alt(abs),
      ...     )

      >>> assert compose_result(IOSuccess(1), count) == IOSuccess(2)
      >>> assert compose_result(IOFailure(-1), count) == IOFailure(1)

    """
    return container.compose_result(function)


#: Kinded version of :func:`~internal_compose_result`,
# use it to infer real return type.
compose_result = kinded(internal_compose_result)
