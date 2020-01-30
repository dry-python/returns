# -*- coding: utf-8 -*-

from returns.context import RequiresContextIOResult, RequiresContextIOResultE


def _function(arg: int) -> RequiresContextIOResultE[int, float]:
    if arg == 0:
        return RequiresContextIOResult.from_failure(
            ZeroDivisionError('Divided by 0'),
        )
    return RequiresContextIOResult.from_success(10 / arg)


def test_requires_context_io_resulte():
    """Ensures that RequiresContextResultE correctly typecast."""
    container: RequiresContextIOResult[int, float, Exception] = _function(1)
    assert container(0) == RequiresContextIOResult.from_success(10.0)(0)
