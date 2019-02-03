# -*- coding: utf-8 -*-

from returns.functions import pipeline
from returns.result import Failure, Result, Success


@pipeline
def _example1(number: int) -> Result[int, str]:
    first = Success(1).unwrap()
    second: int = Success(number).unwrap() if number else Failure('E').unwrap()
    return Success(first + second)


@pipeline
def _example2(number: int) -> Success[int]:
    first: int = Success(1).unwrap()
    return Success(first + Failure(number).unwrap())


def _transformation(number: int) -> Success[int]:
    return Success(-number)


def test_do_notation_success():
    """Ensures that do notation works well for Success."""
    assert _example1(5) == Success(6)
    assert _example1(1).unwrap() == 2
    assert _example1(9).bind(_transformation).value_or(None) == -10


def test_do_notation_failure():
    """Ensures that do notation works well for Failure."""
    assert _example1(0) == Failure('E')
    assert _example2(0) == Failure(0)
    assert _example2(1).rescue(_transformation).unwrap() == -1
