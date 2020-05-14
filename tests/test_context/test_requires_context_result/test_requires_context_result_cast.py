from returns.context import (
    ReaderResult,
    ReaderResultE,
    RequiresContextResult,
    RequiresContextResultE,
)


def _function(arg: int) -> RequiresContextResultE[int, float]:
    if arg == 0:
        return RequiresContextResult.from_failure(
            ZeroDivisionError('Divided by 0'),
        )
    return RequiresContextResult.from_value(10 / arg)


def test_requires_context_resulte():
    """Ensures that RequiresContextResultE correctly typecast."""
    container: RequiresContextResult[int, float, Exception] = _function(1)
    assert container(0) == RequiresContextResult.from_value(10.0)(0)


def test_requires_context_aliases():
    """Ensures that ReaderResult correctly typecast."""
    container: ReaderResultE[int, float] = _function(1)
    container2: ReaderResult[int, float, Exception] = _function(1)
    container3: ReaderResultE[int, float] = ReaderResultE.from_value(
        10.0,
    )
    container4: ReaderResultE[int, float] = ReaderResult.from_value(10.0)

    assert container(0) == container2(0) == container3(0) == container4(0)
    assert container(0) == RequiresContextResult.from_value(10.0)(0)
