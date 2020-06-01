from typing import Callable, TypeVar, Union, overload

from returns.future import FutureResult
from returns.io import IOResult
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType')
_NewErrorType = TypeVar('_NewErrorType')


@overload
def _unify(
    function: Callable[[_ValueType], Result[_NewValueType, _NewErrorType]],
) -> Callable[
    [Result[_ValueType, _ErrorType]],
    Result[_NewValueType, Union[_ErrorType, _NewErrorType]],
]:
    ...


@overload
def _unify(
    function: Callable[[_ValueType], IOResult[_NewValueType, _NewErrorType]],
) -> Callable[
    [IOResult[_ValueType, _ErrorType]],
    IOResult[_NewValueType, Union[_ErrorType, _NewErrorType]],
]:
    ...


@overload
def _unify(
    function: Callable[
        [_ValueType],
        FutureResult[_NewValueType, _NewErrorType],
    ],
) -> Callable[
    [FutureResult[_ValueType, _ErrorType]],
    FutureResult[_NewValueType, Union[_ErrorType, _NewErrorType]],
]:
    ...
