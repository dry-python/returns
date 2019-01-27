# -*- coding: utf-8 -*-

from functools import wraps
from typing import TYPE_CHECKING, Callable, TypeVar

from dry_monads.primitives.exceptions import UnwrapFailedError

if TYPE_CHECKING:
    from dry_monads.primitives.monad import Monad  # noqa: Z435, F401

_MonadType = TypeVar('_MonadType', bound='Monad')


def do_notation(
    function: Callable[..., _MonadType],
) -> Callable[..., _MonadType]:
    """Decorator to enable 'do-notation' context."""
    @wraps(function)
    def decorator(*args, **kwargs) -> _MonadType:
        try:
            return function(*args, **kwargs)
        except UnwrapFailedError as exc:
            return exc.halted_monad
    return decorator
