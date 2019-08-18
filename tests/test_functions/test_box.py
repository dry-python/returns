# -*- coding: utf-8 -*-

from returns.functions import box
from returns.io import IO
from returns.maybe import Maybe, Nothing, Some
from returns.result import Failure, Result, Success


def _io_function(argument: int) -> IO[str]:
    return IO(str(argument + 1))


def _maybe_function(argument: int) -> Maybe[str]:
    return Some(str(argument + 1))


def _result_function(argument: int) -> Result[str, str]:
    return Success(str(argument + 1))


def test_box_with_io():
    """Ensures that functions can be composed and return type is correct."""
    boxed = box(_io_function)

    assert boxed(IO(1)) == IO('2')


def test_box_with_maybe():
    """Ensures that functions can be composed and return type is correct."""
    boxed = box(_maybe_function)

    assert boxed(Some(1)) == Some('2')
    assert boxed(Nothing) == Nothing


def test_box_with_result():
    """Ensures that functions can be composed and return type is correct."""
    boxed = box(_result_function)

    assert boxed(Success(1)) == Success('2')
    assert boxed(Failure('s')) == Failure('s')
