from returns.result import Failure, Success


def test_map_success():
    """Ensures that Success is mappable."""
    assert Success(5).map(str) == Success('5')


def test_alt_failure():
    """Ensures that Failure is mappable."""
    assert Failure(5).map(str) == Failure(5)
    assert Failure(5).alt(str) == Failure('5')


def test_fix_success():
    """Ensures that Success.fix is NoOp."""
    assert Success(5).fix(str) == Success(5)
    assert Success(5).alt(str) == Success(5)


def test_fix_failure():
    """Ensures that Failure.fix produces the Success."""
    assert Failure(5).fix(str) == Success('5')
