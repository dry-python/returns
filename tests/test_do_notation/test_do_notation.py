# -*- coding: utf-8 -*-

from dry_monads.do_notation import do_notation
from dry_monads.either import Either, Failure, Success


@do_notation
def _example(number: int) -> Either[int, str]:
    first = Success(1).unwrap()
    second = Failure('E').unwrap() if number % 2 else Success(number).unwrap()
    return Success(first + second)


def test_do_notation_success():
    """Ensures that do notation works well for Success."""
    assert _example(5) == Success(6)


def test_do_notation_failure():
    """Ensures that do notation works well for Failure."""
    assert _example(6) == Failure('E')
