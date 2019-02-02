# -*- coding: utf-8 -*-

from typing import Callable

from returns.primitives.types import MonadType


def do_notation(
    function: Callable[..., MonadType],
) -> Callable[..., MonadType]:
    ...
