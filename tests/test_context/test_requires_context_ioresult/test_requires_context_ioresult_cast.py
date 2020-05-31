from returns.context import (
    ReaderIOResult,
    ReaderIOResultE,
    RequiresContextIOResult,
    RequiresContextIOResultE,
)


def _function(arg: int) -> RequiresContextIOResultE[int, float]:
    if arg == 0:
        return RequiresContextIOResult.from_failure(
            ZeroDivisionError('Divided by 0'),
        )
    return RequiresContextIOResult.from_value(10 / arg)


def test_requires_context_ioresulte():
    """Ensures that RequiresContextIOResultE correctly typecast."""
    container: RequiresContextIOResult[int, float, Exception] = _function(1)
    assert container(0) == RequiresContextIOResult.from_value(10.0)(0)


def test_requires_context_io_aliases():
    """Ensures that ReaderIOResult correctly typecast."""
    container: ReaderIOResultE[int, float] = _function(1)
    container2: ReaderIOResult[int, float, Exception] = _function(1)
    container3: ReaderIOResultE[int, float] = ReaderIOResultE.from_value(
        10.0,
    )
    container4: ReaderIOResultE[int, float] = ReaderIOResult.from_value(10.0)

    assert container(0) == container2(0) == container3(0) == container4(0)
    assert container(0) == RequiresContextIOResult.from_value(10.0)(0)
