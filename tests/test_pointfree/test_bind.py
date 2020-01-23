# -*- coding: utf-8 -*-

from returns.context import RequiresContext
from returns.io import IO
from returns.maybe import Maybe, Nothing, Some
from returns.pointfree import bind
from returns.result import Failure, Result, Success


def _io_function(argument: int) -> IO[str]:
    return IO(str(argument + 1))


def _maybe_function(argument: int) -> Maybe[str]:
    return Some(str(argument + 1))


def _result_function(argument: int) -> Result[str, str]:
    return Success(str(argument + 1))


def _context_function(argument: int) -> RequiresContext[int, int]:
    return RequiresContext(lambda other: argument + other)


def test_bind_with_io():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_io_function)

    assert binded(IO(1)) == IO('2')


def test_bind_with_maybe():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_maybe_function)

    assert binded(Some(1)) == Some('2')
    assert binded(Nothing) == Nothing


def test_bind_with_result():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_result_function)

    assert binded(Success(1)) == Success('2')
    assert binded(Failure('s')) == Failure('s')


def test_bind_with_context():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_context_function)

    assert binded(RequiresContext(lambda _: 3))(5) == 8
