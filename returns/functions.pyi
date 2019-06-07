# -*- coding: utf-8 -*-

from typing import Callable, Coroutine, NoReturn, TypeVar, overload

from typing_extensions import Literal

from returns.primitives.container import Container
from returns.result import Failure, Result, Success

# Main types:
_ContainerType = TypeVar('_ContainerType', bound=Container)
_ReturnType = TypeVar('_ReturnType')

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

# Hacks:
_ReturnsContainerType = TypeVar(
    '_ReturnsContainerType',
    bound=Callable[..., Container],
)
_ReturnsAsyncContainerType = TypeVar(
    '_ReturnsAsyncContainerType',
    bound=Callable[..., Coroutine[_FirstType, _SecondType, Container]],
)


@overload
def is_successful(container: Success) -> Literal[True]:
    ...


@overload
def is_successful(container: Failure) -> Literal[False]:
    ...


@overload
def is_successful(container: _ContainerType) -> bool:
    ...


# Typing decorators is not an easy task, see:
# https://github.com/python/mypy/issues/3157

@overload
def pipeline(
    function: _ReturnsAsyncContainerType,
) -> _ReturnsAsyncContainerType:
    ...


@overload
def pipeline(function: _ReturnsContainerType) -> _ReturnsContainerType:
    ...


@overload  # noqa: Z320
def safe(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _ReturnType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, Result[_ReturnType, Exception]],
]:
    ...


@overload
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
