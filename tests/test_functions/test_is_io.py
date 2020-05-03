from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.instances import is_io
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result, Success


def test_return_true_with_io_container():
    """Ensures `is_io` function will return True for IO."""
    assert is_io(IO(1.0)) is True


def test_return_true_with_io_result_container():
    """Ensures `is_io` function will return True for IOResult."""
    assert is_io(IOResult(Success(10))) is True


def test_return_true_with_requires_context_io_result_container():  # noqa: E501,WPS118
    """Ensures `is_io` function will return True for RequiresContextIOResult."""
    assert is_io(RequiresContextIOResult.from_success(1.5)) is True


def test_return_false_with_maybe_container():
    """Ensures `is_io` function will return False for Maybe."""
    assert is_io(Maybe.from_value(None)) is False


def test_return_false_with_requires_context_container():  # noqa: WPS118
    """Ensures `is_io` function will return False for RequiresContext."""
    assert is_io(RequiresContext.empty) is False


def test_return_false_with_result_container():
    """Ensures `is_io` function will return False for Result."""
    assert is_io(Result.from_failure('failure')) is False


def test_return_false_with_requires_context_result_container():  # noqa: WPS118
    """Ensures `is_io` function will return False for RequiresContextResult."""
    assert is_io(RequiresContextResult.from_success(Success(True))) is False


def test_return_false_with_future_container():
    """Ensures `is_io` function will return False for Future."""
    assert is_io(Future.from_value('future')) is False


def test_return_false_with_future_result_container():  # noqa: WPS118
    """Ensures `is_io` function will return False for FutureResult."""
    assert is_io(FutureResult.from_failure('failure')) is False
