# -*- coding: utf-8 -*-

from typing import Callable, TypeVar, overload

from returns.io import IO
from returns.maybe import Maybe
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType')


# Box:

@overload
def _box(
    function: Callable[[_ValueType], Maybe[_NewValueType]],
) -> Callable[[Maybe[_ValueType]], Maybe[_NewValueType]]:
    ...


@overload
def _box(
    function: Callable[[_ValueType], IO[_NewValueType]],
) -> Callable[[IO[_ValueType]], IO[_NewValueType]]:
    ...


@overload
def _box(
    function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
) -> Callable[
    [Result[_ValueType, _ErrorType]], Result[_NewValueType, _ErrorType],
]:
    ...
