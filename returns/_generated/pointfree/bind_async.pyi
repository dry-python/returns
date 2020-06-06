from typing import Awaitable, Callable, TypeVar, overload

from returns.context import RequiresContextFutureResult
from returns.future import Future, FutureResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType')


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


@overload
def _bind_async(
    function: Callable[
        [_ValueType],
        Awaitable[RequiresContextFutureResult[
            _EnvType, _NewValueType, _ErrorType,
        ]],
    ],
) -> Callable[
    [RequiresContextFutureResult[_EnvType, _ValueType, _ErrorType]],
    RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType],
]:
    ...
