# -*- coding: utf-8 -*-

from functools import wraps

from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def is_successful(monad):
    """Determins if a monad was a success or not."""
    try:
        monad.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True


def safe(function):
    """
    Decorator to covert exception throwing function to 'Result' monad.

    Show be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.
    """
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            return Success(function(*args, **kwargs))
        except Exception as exc:
            return Failure(exc)
    return decorator
