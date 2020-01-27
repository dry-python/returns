# -*- coding: utf-8 -*-

from returns.io import IOFailure, IOResult, IOSuccess
from returns.pointfree import rescue
from returns.result import Failure, Result, Success


def _result_function(argument: int) -> Result[int, str]:
    if argument > 0:
        return Success(argument + 1)
    return Failure('nope')


def _ioresult_function(argument: int) -> IOResult[int, str]:
    if argument > 0:
        return IOSuccess(argument + 1)
    return IOFailure('nope')


def test_rescue_with_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    rescued = rescue(_ioresult_function)

    assert rescued(IOSuccess(1)) == IOSuccess(1)
    assert rescued(IOFailure(1)) == IOSuccess(2)
    assert rescued(IOFailure(0)) == IOFailure('nope')


def test_rescue_with_result():
    """Ensures that functions can be composed and return type is correct."""
    rescued = rescue(_result_function)

    assert rescued(Success(1)) == Success(1)
    assert rescued(Failure(1)) == Success(2)
    assert rescued(Failure(0)) == Failure('nope')
