import pytest

from returns.future import asyncize


@asyncize
def _function(arg: int) -> float:
    return arg / 2


@pytest.mark.anyio
async def test_asyncize_decorator():
    """Ensure that function marked with ``@asyncize`` is awaitable."""
    coro = _function(1)

    assert await coro == 0.5
