import pytest

from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import pipeline


@pipeline(Maybe)
def _maybe_pipeline(number: int) -> Maybe[int]:
    first: int = Some(number).unwrap() if number else Nothing.unwrap()
    return Some(first + number)


@pipeline(Maybe)
async def _async_maybe_pipeline(number: int) -> Maybe[int]:
    first: int = Some(number).unwrap() if number else Nothing.unwrap()
    return Some(first + number)


def test_maybe_pipeline_some():
    """Ensures that pipeline works well for Some."""
    assert _maybe_pipeline(1) == Some(2)
    assert _maybe_pipeline(0) == Nothing


@pytest.mark.anyio
async def test_async_maybe_pipeline_some():
    """Ensures that pipeline works well for Some."""
    assert (await _async_maybe_pipeline(1)) == Some(2)
    assert (await _async_maybe_pipeline(0)) == Nothing
