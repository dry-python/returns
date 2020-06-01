from returns.context import RequiresContextIOResult, RequiresContextResult
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


def _context_result_function(
    argument: int,
) -> RequiresContextResult[int, int, str]:
    if argument > 0:
        return RequiresContextResult(lambda deps: Success(argument + deps))
    return RequiresContextResult.from_failure('nope')


def _context_ioresult_function(
    argument: int,
) -> RequiresContextIOResult[int, int, str]:
    if argument > 0:
        return RequiresContextIOResult(lambda deps: IOSuccess(argument + deps))
    return RequiresContextIOResult.from_failure('nope')


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


def test_rescue_with_context_result():
    """Ensures that functions can be composed and return type is correct."""
    rescued = rescue(_context_result_function)

    assert rescued(
        RequiresContextResult.from_value(1),
    )(1) == Success(1)
    assert rescued(
        RequiresContextResult.from_failure(1),
    )(1) == Success(2)
    assert rescued(
        RequiresContextResult.from_failure(0),
    )(1) == Failure('nope')


def test_rescue_with_context_ioresult():
    """Ensures that functions can be composed and return type is correct."""
    rescued = rescue(_context_ioresult_function)

    assert rescued(
        RequiresContextIOResult.from_value(1),
    )(1) == IOSuccess(1)
    assert rescued(
        RequiresContextIOResult.from_failure(1),
    )(1) == IOSuccess(2)
    assert rescued(
        RequiresContextIOResult.from_failure(0),
    )(1) == IOFailure('nope')
