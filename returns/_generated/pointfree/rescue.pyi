# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

from returns.io import IOResult
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType')
_NewErrorType = TypeVar('_NewErrorType')


@overload
def _rescue(
    function: Callable[[_ErrorType], Result[_ValueType, _NewErrorType]],
) -> Callable[
    [Result[_ValueType, _ErrorType]],
    Result[_ValueType, _NewErrorType],
]:
    ...


@overload
def _rescue(
    function: Callable[[_ErrorType], IOResult[_ValueType, _NewErrorType]],
) -> Callable[
    [IOResult[_ValueType, _ErrorType]],
    IOResult[_ValueType, _NewErrorType],
]:
    ...
