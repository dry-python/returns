# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable

from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.types import MonadType

# Typing decorators is not an easy task, see:
# https://github.com/python/mypy/issues/3157


def do_notation(
    function: Callable[..., MonadType],
) -> Callable[..., MonadType]:
    """
    Decorator to enable 'do-notation' context.

    Should be used for series of computations that rely on ``.unwrap`` method.
    """
    @wraps(function)
    def decorator(*args, **kwargs) -> MonadType:
        try:
            return function(*args, **kwargs)
        except UnwrapFailedError as exc:
            return exc.halted_monad
    return decorator
