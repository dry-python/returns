from typing import Callable, TypeVar

from returns.future import FutureResult
from returns.interfaces.specific.future_result import FutureResultLikeN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_FutureResultKind = TypeVar('_FutureResultKind', bound=FutureResultLikeN)


@kinded
def bind_future_result(
    container: KindN[_FutureResultKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], FutureResult[_UpdatedType, _SecondType]],
) -> KindN[_FutureResultKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a function returning ``FutureResult`` over a container.

    .. code:: python

        >>> import anyio
        >>> from returns.future import FutureResult
        >>> from returns.context import ReaderFutureResult
        >>> from returns.io import IOSuccess, IOFailure
        >>> from returns.methods import bind_future_result

        >>> def function(x: int) -> FutureResult[str, int]:
        ...    return FutureResult.from_value(str(x + 1))

        >>> bound = bind_future_result(
        ...     ReaderFutureResult.from_value(1), function,
        ... )
        >>> assert anyio.run(bound, ReaderFutureResult.empty) == IOSuccess('2')

        >>> bound = bind_future_result(
        ...     ReaderFutureResult.from_failure(1), function,
        ... )
        >>> assert anyio.run(bound, ReaderFutureResult.empty) == IOFailure(1)

    Note, that this function works
    for all containers with ``.bind_future_result`` method.
    See :class:`returns.primitives.interfaces.specific.future.FutureResultLikeN`
    for more info.

    """
    return container.bind_future_result(function)
