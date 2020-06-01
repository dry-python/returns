import pytest

from returns.future import asyncify


@asyncify
def _function(arg: int) -> float:
    return arg / 2


@pytest.mark.anyio
async def test_asyncify_decorator():
    """Ensure that function marked with ``@asyncify`` is awaitable."""
    coro = _function(1)

    assert await coro == 0.5
