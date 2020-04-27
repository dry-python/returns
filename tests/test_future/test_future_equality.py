import pytest

from returns.future import Future


def test_nonequality():
    """Ensures that containers can be compared."""
    assert Future.from_value(1) != Future.from_value(1)
    assert hash(Future.from_value(1))


@pytest.mark.anyio
async def test_equality():
    """Ensures that containers are not compared to regular values."""
    assert await Future.from_value(2) == await Future.from_value(2)
