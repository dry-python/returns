from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.reader_result import ReaderResultLikeN
from returns.primitives.hkt import KindN, kinded

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


@kinded
def bind_context_result(
    container: KindN[
        _ReaderResultLikeKind,
        _FirstType,
        _SecondType,
        _ThirdType,
    ],
    function: Callable[
        [_FirstType],
        'ReaderResult[_UpdatedType, _SecondType, _ThirdType]',
    ],
) -> KindN[_ReaderResultLikeKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``ReaderResult`` returning function over a container.

    .. code:: python

      >>> from returns.methods import bind_context_result
      >>> from returns.context import ReaderIOResult, ReaderResult
      >>> from returns.io import IOSuccess, IOFailure

      >>> def example(argument: int) -> ReaderResult[int, str, str]:
      ...     return ReaderResult.from_value(argument + 1)

      >>> assert bind_context_result(
      ...     ReaderIOResult.from_value(1), example,
      ... )(...) == IOSuccess(2)
      >>> assert bind_context_result(
      ...     ReaderIOResult.from_failure('a'), example,
      ... )(...) == IOFailure('a')

    Note, that this function works
    for all containers with ``.bind_context_result`` method.
    See :class:`returns.primitives.interfaces.specific.result.ResultLikeN`
    for more info.

    """
    return container.bind_context_result(function)
