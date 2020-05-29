from typing import Awaitable, Callable, TypeVar, overload

from returns.future import Future, FutureResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)


@overload
def _bind_async(
    function: Callable[[_ValueType], Awaitable[Future[_NewValueType]]],
) -> Callable[[Future[_ValueType]], Future[_NewValueType]]:
    ...


@overload
def _bind_async(
    function: Callable[
        [_ValueType],
        Awaitable[FutureResult[_NewValueType, _ErrorType]],
    ],
) -> Callable[
    [FutureResult[_ValueType, _ErrorType]],
    FutureResult[_NewValueType, _ErrorType],
]:
    ...
