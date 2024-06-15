import pytest

from returns.future import FutureResult


def test_nonequality():
    """Ensures that containers can be compared."""
    assert FutureResult.from_value(1) != FutureResult.from_value(1)
    assert hash(FutureResult.from_value(1))


@pytest.mark.anyio
async def test_equality():
    """Ensures that containers are not compared to regular values."""
    assert await FutureResult.from_value(
        2,
    ) == await FutureResult.from_value(2)
