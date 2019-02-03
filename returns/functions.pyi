# -*- coding: utf-8 -*-

from typing import Callable, TypeVar

from returns.primitives.monad import Monad
from returns.result import Result

_MonadType = TypeVar('_MonadType', bound=Monad)
_ReturnsMonadType = TypeVar('_ReturnsMonadType', bound=Callable[..., Monad])
_ReturnType = TypeVar('_ReturnType')


def is_successful(monad: _MonadType) -> bool:
    ...


# Typing decorators is not an easy task, see:
# https://github.com/python/mypy/issues/3157

def pipeline(function: _ReturnsMonadType) -> _ReturnsMonadType:
    ...


def safe(
    function: Callable[..., _ReturnType],
) -> Callable[..., Result[_ReturnType, Exception]]:
    ...
