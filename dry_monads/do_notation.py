# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable

from dry_monads.primitives.exceptions import UnwrapFailedError
from dry_monads.primitives.types import MonadType


def do_notation(
    function: Callable[..., MonadType],
) -> Callable[..., MonadType]:
    """Decorator to enable 'do-notation' context."""
    @wraps(function)
    def decorator(*args, **kwargs) -> MonadType:
        try:
            return function(*args, **kwargs)
        except UnwrapFailedError as exc:
            return exc.halted_monad
    return decorator
