import pytest

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.maybe import Maybe, Nothing, Some
from returns.pointfree import apply
from returns.result import Failure, Result, Success


def _function(argument: int) -> str:
    return str(argument + 1)


def test_apply_with_io():
    """Ensures that functions can be composed and return type is correct."""
    assert apply(IO(_function))(IO(1)) == IO('2')


def test_apply_with_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(IOResult.from_value(_function))

    assert applied(IOSuccess(1)) == IOSuccess('2')
    assert applied(IOFailure('a')) == IOFailure('a')


def test_apply_with_maybe():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(Maybe.from_value(_function))

    assert applied(Some(1)) == Some('2')
    assert applied(Nothing) == Nothing


def test_apply_with_result():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(Result.from_value(_function))

    assert applied(Success(1)) == Success('2')
    assert applied(Failure('s')) == Failure('s')


def test_apply_with_context():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(RequiresContext.from_value(_function))

    assert applied(RequiresContext.from_value(1))(...) == '2'


def test_apply_with_context_result():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(RequiresContextResult.from_value(_function))

    assert applied(
        RequiresContextResult.from_value(1),
    )(...) == Success('2')


def test_apply_with_context_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    applied = apply(RequiresContextIOResult.from_value(_function))

    assert applied(
        RequiresContextIOResult.from_value(1),
    )(...) == IOSuccess('2')


@pytest.mark.anyio
async def test_apply_future():
    """Ensures that functions can be composed and return type is correct."""
    assert await apply(
        Future.from_value(_function),
    )(Future.from_value(1)) == IO('2')


@pytest.mark.anyio
async def test_apply_future_result():
    """Ensures that functions can be composed and return type is correct."""
    assert await apply(
        FutureResult.from_value(_function),
    )(FutureResult.from_value(1)) == IOSuccess('2')
    assert await apply(
        FutureResult.from_value(_function),
    )(FutureResult.from_failure(1)) == IOFailure(1)
