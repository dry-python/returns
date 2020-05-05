import pytest

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.instances import is_result
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result, Success


def test_return_false_with_io_container():
    """Ensures `is_result` function will return False for IO."""
    assert is_result(IO(1.0)) is False


def test_return_true_with_io_result_container():
    """Ensures `is_result` function will return True for IOResult."""
    assert is_result(IOResult(Success(10))) is True


def test_return_true_with_requires_context_io_result_container():  # noqa: E501,WPS118
    """Ensures `is_result` function will return True for RequiresContextIOResult."""  # noqa: E501
    assert is_result(RequiresContextIOResult.from_success(1.5)) is True


def test_return_false_with_maybe_container():
    """Ensures `is_result` function will return False for Maybe."""
    assert is_result(Maybe.from_value(None)) is False


def test_return_false_with_requires_context_container():  # noqa: WPS118
    """Ensures `is_result` function will return False for RequiresContext."""
    assert is_result(RequiresContext.empty) is False


def test_return_true_with_result_container():
    """Ensures `is_result` function will return True for Result."""
    assert is_result(Result.from_failure('failure')) is True


def test_return_true_with_requires_context_result_container():  # noqa: WPS118
    """Ensures `is_result` function will return True for RequiresContextResult."""  # noqa: E501
    assert is_result(RequiresContextResult.from_success(Success(True))) is True


def test_return_false_with_future_container():
    """Ensures `is_result` function will return False for Future."""
    assert is_result(Future.from_value('future')) is False


@pytest.mark.anyio  # noqa: WPS118
async def test_return_false_with_awaited_future_container():  # noqa: WPS118
    """Ensures `is_result` function will return False for Future."""
    assert is_result(await Future.from_value('future')) is False


def test_return_true_with_future_result_container():
    """Ensures `is_result` function will return True for FutureResult."""
    assert is_result(FutureResult.from_failure('failure')) is True


@pytest.mark.anyio  # noqa: WPS118
async def test_return_true_with_awaited_future_result_container():  # noqa: E501,WPS118
    """Ensures `is_result` function will return True for FutureResult."""
    assert is_result(await FutureResult.from_failure('failure')) is True
