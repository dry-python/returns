from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.reader_result import ReaderResultLikeN
from returns.primitives.hkt import Kinded, KindN, kinded

if TYPE_CHECKING:
    from returns.context import ReaderResult  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ReaderResultLikeKind = TypeVar(
    '_ReaderResultLikeKind',
    bound=ReaderResultLikeN,
)


def bind_context_result(
    function: Callable[
        [_FirstType],
        'ReaderResult[_UpdatedType, _SecondType, _ThirdType]',
    ],
) -> Kinded[Callable[
    [KindN[_ReaderResultLikeKind, _FirstType, _SecondType, _ThirdType]],
    KindN[_ReaderResultLikeKind, _UpdatedType, _SecondType, _ThirdType],
]]:
    """
    Composes successful container with a function that returns a container.

    In other words, it modifies the function's
    signature from: ``a -> ReaderResult[b, c, e]``
    to: ``Container[a, c, e] -> Container[b, c, e]``

    .. code:: python

      >>> from returns.io import IOSuccess
      >>> from returns.context import RequiresContextResult
      >>> from returns.result import Result, Success
      >>> from returns.pointfree import bind_result

      >>> def returns_result(arg: int) -> Result[int, str]:
      ...     return Success(arg + 1)

      >>> bound = bind_result(returns_result)
      >>> assert bound(IOSuccess(1)) == IOSuccess(2)
      >>> assert bound(RequiresContextResult.from_value(1))(...) == Success(2)

    """
    @kinded
    def factory(
        container: KindN[
            _ReaderResultLikeKind,
            _FirstType,
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[_ReaderResultLikeKind, _UpdatedType, _SecondType, _ThirdType]:
        return container.bind_context_result(function)
    return factory
