# -*- coding: utf-8 -*-

from typing import Callable, TypeVar

from returns.primitives.types import MonadType
from returns.result import Result

_ReturnType = TypeVar('_ReturnType')


def is_successful(monad: MonadType) -> bool:
    ...


def safe(
    function: Callable[..., _ReturnType],
) -> Callable[..., Result[_ReturnType, Exception]]:
    ...
