import pytest

from returns.pipeline import pipeline
from returns.result import Result, Success, safe


@safe
def _divide(number: int) -> float:
    return number / number


@safe
def _sum(first: int, second: float) -> float:
    return first + second


@pipeline(Result)
def _result_pipeline(number: int) -> Result[float, Exception]:
    divided = _divide(number).unwrap()
    return _sum(number, divided)


@pipeline(Result)
async def _result_async_pipeline(number: int) -> Result[float, Exception]:
    divided = _divide(number).unwrap()
    return _sum(number, divided)


def test_pipeline():
    """Ensures that pipeline works well for sync functions."""
    assert _result_pipeline(1) == Success(2.0)
    with pytest.raises(ZeroDivisionError):
        raise _result_pipeline(0).failure()


@pytest.mark.anyio
async def test_async_pipeline():
    """Ensures that async pipeline works well for async functions."""
    assert (await _result_async_pipeline(1)) == Success(2.0)
    with pytest.raises(ZeroDivisionError):
        raise (await _result_async_pipeline(0)).failure()
