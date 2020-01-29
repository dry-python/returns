# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

from returns.context import RequiresContextResult
from returns.io import IOResult
from returns.result import Result

# Result:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType')
_NewErrorType = TypeVar('_NewErrorType')

# Context:
_EnvType = TypeVar('_EnvType')


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


@overload
def _rescue(
    function: Callable[
        [_ErrorType],
        RequiresContextResult[_EnvType, _ValueType, _NewErrorType],
    ],
) -> Callable[
    [RequiresContextResult[_EnvType, _ValueType, _ErrorType]],
    RequiresContextResult[_EnvType, _ValueType, _NewErrorType],
]:
    ...
