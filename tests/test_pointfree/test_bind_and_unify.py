import pytest

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.maybe import Maybe, Nothing, Some
from returns.pointfree import bind, unify
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


def _context_ioresult_function(
    argument: int,
) -> RequiresContextIOResult[int, int, str]:
    return RequiresContextIOResult(lambda other: IOSuccess(argument + other))


def _future_function(argument: int) -> Future[str]:
    return Future.from_value(str(argument + 1))


def _future_result_function(argument: int) -> FutureResult[str, float]:
    return FutureResult.from_value(str(argument + 1))


def test_bind_with_io():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_io_function)

    assert bound(IO(1)) == IO('2')


def test_bind_with_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_ioresult_function)

    assert bound(IOSuccess(1)) == IOSuccess('2')
    assert bound(IOFailure('a')) == IOFailure('a')
    assert bound(IOSuccess(1)) == unify(_ioresult_function)(IOSuccess(1))


def test_bind_with_maybe():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_maybe_function)

    assert bound(Some(1)) == Some('2')
    assert bound(Nothing) == Nothing


def test_bind_with_result():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_result_function)

    assert bound(Success(1)) == Success('2')
    assert bound(Failure('s')) == Failure('s')
    assert bound(Success(1)) == unify(_result_function)(Success(1))


def test_bind_with_context():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_context_function)

    assert bound(RequiresContext(lambda _: 3))(5) == 8


def test_bind_with_context_result():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_context_result_function)

    assert bound(RequiresContextResult.from_value(3))(5) == Success(8)


def test_bind_with_context_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    bound = bind(_context_ioresult_function)

    assert bound(RequiresContextIOResult.from_value(3))(5) == IOSuccess(8)


@pytest.mark.anyio
async def test_bind_future():
    """Ensures that functions can be composed and return type is correct."""
    assert await bind(_future_function)(Future.from_value(1)) == IO('2')


@pytest.mark.anyio
async def test_bind_future_result():
    """Ensures that functions can be composed and return type is correct."""
    assert await bind(_future_result_function)(
        FutureResult.from_value(1),
    ) == IOSuccess('2')
    assert await bind(_future_result_function)(
        FutureResult.from_failure(1.0),
    ) == IOFailure(1.0)
