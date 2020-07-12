from typing import Callable, TypeVar, overload

from returns.context import ReaderFutureResult, ReaderIOResult
from returns.future import FutureResult
from returns.io import IOResult
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_EnvType = TypeVar('_EnvType', contravariant=True)


@overload
def _managed(
    use: Callable[
        [_ValueType],
        IOResult[_NewValueType, _ErrorType],
    ],
    release: Callable[
        [_ValueType, Result[_NewValueType, _ErrorType]],
        IOResult[None, _ErrorType],
    ],
) -> Callable[
    [IOResult[_ValueType, _ErrorType]],
    IOResult[_NewValueType, _ErrorType],
]:
    ...


@overload
def _managed(
    use: Callable[
        [_ValueType],
        FutureResult[_NewValueType, _ErrorType],
    ],
    release: Callable[
        [_ValueType, Result[_NewValueType, _ErrorType]],
        FutureResult[None, _ErrorType],
    ],
) -> Callable[
    [FutureResult[_ValueType, _ErrorType]],
    FutureResult[_NewValueType, _ErrorType],
]:
    ...


@overload
def _managed(
    use: Callable[
        [_ValueType],
        ReaderIOResult[_NewValueType, _ErrorType, _EnvType],
    ],
    release: Callable[
        [_ValueType, Result[_NewValueType, _ErrorType]],
        ReaderIOResult[None, _ErrorType, _EnvType],
    ],
) -> Callable[
    [ReaderIOResult[_ValueType, _ErrorType, _EnvType]],
    ReaderIOResult[_NewValueType, _ErrorType, _EnvType],
]:
    ...


@overload
def _managed(
    use: Callable[
        [_ValueType],
        ReaderFutureResult[_NewValueType, _ErrorType, _EnvType],
    ],
    release: Callable[
        [_ValueType, Result[_NewValueType, _ErrorType]],
        ReaderFutureResult[None, _ErrorType, _EnvType],
    ],
) -> Callable[
    [ReaderFutureResult[_ValueType, _ErrorType, _EnvType]],
    ReaderFutureResult[_NewValueType, _ErrorType, _EnvType],
]:
    ...
