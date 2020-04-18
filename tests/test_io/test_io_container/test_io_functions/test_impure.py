import pytest

from returns.io import IO, impure


def _fake_impure_function(some_param: int) -> int:
    return some_param


async def _fake_impure_coroutine(some_param: int) -> int:
    return some_param


def test_impure():
    """Ensures that impure returns IO container."""
    impure_result = impure(_fake_impure_function)(1)
    assert isinstance(impure_result, IO)
    assert impure_result == IO(1)


@pytest.mark.asyncio
async def test_impure_async():
    """Ensures that impure returns IO container for async."""
    impure_result = await impure(_fake_impure_coroutine)(1)
    assert isinstance(impure_result, IO)
    assert impure_result == IO(1)
