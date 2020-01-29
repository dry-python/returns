# -*- coding: utf-8 -*-

from returns.context import RequiresContextResult, RequiresContextResultE


def _function(arg: int) -> RequiresContextResultE[int, float]:
    if arg == 0:
        return RequiresContextResult.from_failure(
            ZeroDivisionError('Divided by 0'),
        )
    return RequiresContextResult.from_success(10 / arg)


def test_requires_context_resulte():
    """Ensures that RequiresContextResultE correctly typecast."""
    container: RequiresContextResult[int, float, Exception] = _function(1)
    assert container(0) == RequiresContextResult.from_success(10.0)(0)
