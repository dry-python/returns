# -*- coding: utf-8 -*-

from typing import Callable, TypeVar

from returns.primitives.monad import Monad

_ReturnsMonad = TypeVar('_ReturnsMonad', bound=Callable[..., Monad])


def do_notation(
    function: _ReturnsMonad,
) -> _ReturnsMonad:
    ...
