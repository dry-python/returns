# -*- coding: utf-8 -*-

from typing import Callable, NoReturn, TypeVar

from returns.primitives.container import Container
from returns.result import Result

_ContainerType = TypeVar('_ContainerType', bound=Container)
_ReturnType = TypeVar('_ReturnType')
_ReturnsContainerType = TypeVar(
    '_ReturnsContainerType',
    bound=Callable[..., Container],
)

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


def is_successful(container: _ContainerType) -> bool:
    ...


# Typing decorators is not an easy task, see:
# https://github.com/python/mypy/issues/3157

def pipeline(function: _ReturnsContainerType) -> _ReturnsContainerType:
    ...


def safe(
    function: Callable[..., _ReturnType],
) -> Callable[..., Result[_ReturnType, Exception]]:
    ...


def compose(
    first: Callable[[_FirstType], _SecondType],
    second: Callable[[_SecondType], _ThirdType],
) -> Callable[[_FirstType], _ThirdType]:
    ...


def raise_exception(exception: Exception) -> NoReturn:
    ...
