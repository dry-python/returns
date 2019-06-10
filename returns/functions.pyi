# -*- coding: utf-8 -*-

from typing import Callable, NoReturn, TypeVar

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


def compose(
    first: Callable[[_FirstType], _SecondType],
    second: Callable[[_SecondType], _ThirdType],
) -> Callable[[_FirstType], _ThirdType]:
    ...


def raise_exception(exception: Exception) -> NoReturn:
    ...
