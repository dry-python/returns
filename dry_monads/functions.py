# -*- coding: utf-8 -*-

from functools import wraps
from typing import Callable, TypeVar

from dry_monads.either import Either, Failure, Success
from dry_monads.primitives.exceptions import UnwrapFailedError
from dry_monads.primitives.types import MonadType

_ReturnType = TypeVar('_ReturnType')


def is_successful(monad: MonadType) -> bool:
    """Determins if a monad was a success or not."""
    try:
        monad.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True


def safe(
    function: Callable[..., _ReturnType],
) -> Callable[..., Either[_ReturnType, Exception]]:
    """
    Decorator to covert exception throwing function to 'Either' monad.

    Show be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.
    """
    @wraps(function)
    def decorator(*args, **kwargs) -> Either[_ReturnType, Exception]:
        try:
            return Success(function(*args, **kwargs))
        except Exception as exc:
            return Failure(exc)
    return decorator
