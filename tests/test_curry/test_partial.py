from collections.abc import Callable
from typing import TypeAlias, TypeVar, cast

from returns.curry import partial

_ReturnType = TypeVar('_ReturnType')
_Decorator: TypeAlias = Callable[
    [Callable[..., _ReturnType]],
    Callable[..., _ReturnType],
]


def add(first: int, second: int) -> int:
    return first + second


def test_partial_direct_call() -> None:
    add_one = partial(add, 1)
    assert add_one(2) == 3


def test_partial_as_decorator_factory() -> None:
    decorator = cast(_Decorator[int], partial())
    add_with_decorator = decorator(add)
    assert add_with_decorator(1, 2) == 3


def test_partial_with_none_placeholder() -> None:
    decorator = cast(_Decorator[int], partial(None, 1))
    add_with_none_decorator = decorator(add)
    assert add_with_none_decorator(2) == 3
