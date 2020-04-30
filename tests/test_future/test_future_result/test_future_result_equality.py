import pytest

from returns.future import FutureResult


def test_nonequality():
    """Ensures that containers can be compared."""
    assert FutureResult.from_success(1) != FutureResult.from_success(1)
    assert hash(FutureResult.from_success(1))


@pytest.mark.anyio
async def test_equality():
    """Ensures that containers are not compared to regular values."""
    assert await FutureResult.from_success(
        2,
    ) == await FutureResult.from_success(2)
