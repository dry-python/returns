# -*- coding: utf-8 -*-

from typing import Callable, Coroutine, TypeVar, Union, overload

from returns.maybe import Maybe
from returns.result import Result

# Logical aliases:
_Unwrapable = Union[Result, Maybe]

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')

# Hacks for functions:
_ReturnsResultType = TypeVar(
    '_ReturnsResultType',
    bound=Callable[..., _Unwrapable],
)
_AsyncReturnsResultType = TypeVar(
    '_AsyncReturnsResultType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, _Unwrapable]],
)


def is_successful(container: _Unwrapable) -> bool:
    ...


@overload
def pipeline(
    function: _AsyncReturnsResultType,
) -> _AsyncReturnsResultType:
    ...


@overload
def pipeline(function: _ReturnsResultType) -> _ReturnsResultType:
    ...
