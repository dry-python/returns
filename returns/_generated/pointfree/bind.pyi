# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

from returns.context import RequiresContext, RequiresContextResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType')
_EnvType = TypeVar('_EnvType')


# Bind:

@overload
def _bind(
    function: Callable[[_ValueType], Maybe[_NewValueType]],
) -> Callable[[Maybe[_ValueType]], Maybe[_NewValueType]]:
    ...


@overload
def _bind(
    function: Callable[[_ValueType], IO[_NewValueType]],
) -> Callable[[IO[_ValueType]], IO[_NewValueType]]:
    ...


@overload
def _bind(
    function: Callable[[_ValueType], RequiresContext[_EnvType, _NewValueType]],
) -> Callable[
    [RequiresContext[_EnvType, _ValueType]],
    RequiresContext[_EnvType, _NewValueType],
]:
    ...


@overload
def _bind(
    function: Callable[
        [_ValueType],
        RequiresContextResult[_EnvType, _NewValueType, _ErrorType],
    ],
) -> Callable[
    [RequiresContextResult[_EnvType, _ValueType, _ErrorType]],
    RequiresContextResult[_EnvType, _NewValueType, _ErrorType],
]:
    ...


@overload
def _bind(
    function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
) -> Callable[
    [Result[_ValueType, _ErrorType]],
    Result[_NewValueType, _ErrorType],
]:
    ...


@overload
def _bind(
    function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
) -> Callable[
    [IOResult[_ValueType, _ErrorType]],
    IOResult[_NewValueType, _ErrorType],
]:
    ...
