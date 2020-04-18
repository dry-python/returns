from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.maybe import Maybe, Nothing, Some
from returns.pointfree import bind
from returns.result import Failure, Result, Success


def _io_function(argument: int) -> IO[str]:
    return IO(str(argument + 1))


def _maybe_function(argument: int) -> Maybe[str]:
    return Some(str(argument + 1))


def _result_function(argument: int) -> Result[str, str]:
    return Success(str(argument + 1))


def _ioresult_function(argument: int) -> IOResult[str, str]:
    return IOSuccess(str(argument + 1))


def _context_function(argument: int) -> RequiresContext[int, int]:
    return RequiresContext(lambda other: argument + other)


def _context_result_function(
    argument: int,
) -> RequiresContextResult[int, int, str]:
    return RequiresContextResult(lambda other: Success(argument + other))


def _context_io_result_function(
    argument: int,
) -> RequiresContextIOResult[int, int, str]:
    return RequiresContextIOResult(lambda other: IOSuccess(argument + other))


def test_bind_with_io():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_io_function)

    assert binded(IO(1)) == IO('2')


def test_bind_with_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_ioresult_function)

    assert binded(IOSuccess(1)) == IOSuccess('2')
    assert binded(IOFailure('a')) == IOFailure('a')


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


def test_bind_with_context_result():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_context_result_function)

    assert binded(RequiresContextResult.from_success(3))(5) == Success(8)


def test_bind_with_context_io_result():
    """Ensures that functions can be composed and return type is correct."""
    binded = bind(_context_io_result_function)

    assert binded(RequiresContextIOResult.from_success(3))(5) == IOSuccess(8)
