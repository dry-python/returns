# -*- coding: utf-8 -*-

from typing import Callable, TypeVar

from returns.either import Either
from returns.primitives.types import MonadType

_ReturnType = TypeVar('_ReturnType')


def is_successful(monad: MonadType) -> bool:
    ...


def safe(
    function: Callable[..., _ReturnType],
) -> Callable[..., Either[_ReturnType, Exception]]:
    ...
