# -*- coding: utf-8 -*-

from functools import wraps

from returns.primitives.exceptions import UnwrapFailedError


def do_notation(function):
    """
    Decorator to enable 'do-notation' context.

    Should be used for series of computations that rely on ``.unwrap`` method.
    """
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except UnwrapFailedError as exc:
            return exc.halted_monad
    return decorator
