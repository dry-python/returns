import pytest

from returns.future import Future, future
from returns.io import IO


@future
async def _coro(arg: int) -> float:
    return arg / 2


@pytest.mark.anyio
async def test_safe_decorator():
    """Ensure that coroutine marked with ``@future`` returns ``Future``."""
    future_instance = _coro(1)

    assert isinstance(future_instance, Future)
    assert await future_instance == IO(0.5)
