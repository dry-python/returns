# -*- coding: utf-8 -*-

from typing import Callable

from returns.primitives.types import MonadType

# Typing decorators is not an easy task, see:
# https://github.com/python/mypy/issues/3157


def do_notation(
    function: Callable[..., MonadType],
) -> Callable[..., MonadType]:
    ...
