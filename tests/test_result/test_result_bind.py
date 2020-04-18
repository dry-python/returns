from returns.result import Failure, Result, Success


def test_bind():
    """Ensures that bind works."""
    def factory(inner_value: int) -> Result[int, str]:
        if inner_value > 0:
            return Success(inner_value * 2)
        return Failure(str(inner_value))

    input_value = 5
    bound: Result[int, str] = Success(input_value)

    assert bound.bind(factory) == factory(input_value)
    assert Success(input_value).bind(factory) == factory(input_value)
    assert str(bound.bind(factory)) == '<Success: 10>'

    input_value = 0
    bound2: Result[int, str] = Success(input_value)

    assert bound2.bind(factory) == factory(input_value)
    assert str(bound2.bind(factory)) == '<Failure: 0>'


def test_left_identity_success():
    """Ensures that left identity works for Success container."""
    def factory(inner_value: int) -> Result[int, str]:
        return Success(inner_value * 2)

    input_value = 5
    bound: Result[int, str] = Success(input_value)

    assert bound.bind(factory) == factory(input_value)


def test_unify_and_bind():
    """Ensures that left identity works for Success container."""
    def factory(inner_value: int) -> Result[int, str]:
        return Success(inner_value * 2)

    bound: Result[int, str] = Success(5)

    assert bound.unify(factory) == bound.bind(factory)
    assert bound.bind(factory) == bound.unify(factory)


def test_left_identity_failure():
    """Ensures that left identity works for Failure container."""
    def factory(inner_value: int) -> Result[int, int]:
        return Failure(6)

    input_value = 5
    bound: Result[int, int] = Failure(input_value)

    assert bound.bind(factory) == Failure(input_value)
    assert Failure(input_value).bind(factory) == Failure(5)
    assert bound.unify(factory) == Failure(input_value)
    assert str(bound) == '<Failure: 5>'


def test_rescue_success():
    """Ensures that rescue works for Success container."""
    def factory(inner_value) -> Result[int, str]:
        return Success(inner_value * 2)

    bound = Success(5).rescue(factory)

    assert bound == Success(5)
    assert Success(5).rescue(factory) == Success(5)
    assert str(bound) == '<Success: 5>'


def test_rescue_failure():
    """Ensures that rescue works for Failure container."""
    def factory(inner_value: int) -> Result[str, int]:
        return Failure(inner_value + 1)

    expected = 6
    bound: Result[str, int] = Failure(5)

    assert bound.rescue(factory) == Failure(expected)
    assert Failure(5).rescue(factory) == Failure(expected)
    assert str(bound.rescue(factory)) == '<Failure: 6>'
