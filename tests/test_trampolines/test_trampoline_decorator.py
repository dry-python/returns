import sys
from collections.abc import Callable, Iterator
from typing import Union

import pytest

from returns.trampolines import Trampoline, trampoline


@trampoline
def _accumulate(
    numbers: Iterator[int],
    acc: int = 0,
) -> int | Trampoline[int]:
    number = next(numbers, None)
    if number is None:
        return acc
    return Trampoline(_accumulate, numbers, acc + number)


@trampoline
def _with_func_kwarg(
    numbers: Iterator[int],
    func: int = 0,  # we need this name to match `Trampoline` constructor
) -> int | Trampoline[int]:
    number = next(numbers, None)
    if number is None:
        return func
    return Trampoline(_with_func_kwarg, numbers, func=func + number)


@pytest.mark.parametrize('trampoline_func', [
    _accumulate,
    _with_func_kwarg,
])
@pytest.mark.parametrize('given_range', [
    range(0),
    range(1),
    range(2),
    range(5),
    range(sys.getrecursionlimit()),
    range(sys.getrecursionlimit() + 1),
])
def test_recursion_limit(
    trampoline_func: Callable[[Iterator[int]], int],
    given_range: range,
) -> None:
    """Test that accumulation is correct and no ``RecursionError`` happens."""
    accumulated = trampoline_func(iter(given_range))

    assert accumulated == sum(given_range)
