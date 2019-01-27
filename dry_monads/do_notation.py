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

# from dry_monads.either import Success, Failure, Either

# @do_notation
# def test() -> Success[int]:
#     def example(incoming: int) -> Either[int, int]:
#         return Failure("abc")

#     first = example(1).unwrap()
#     second = example(2).unwrap()
#     reveal_type(first)  # dry_monads/do.py:35: error: Revealed type is 'builtins.int*'
#     reveal_type(second)  # dry_monads/do.py:36: error: Revealed type is 'builtins.int*'
#     return Success(first + second)

# reveal_type(test())  # dry_monads/do.py:39: error: Revealed type is 'dry_monads.either.Right*[builtins.int]'
# print(test())
