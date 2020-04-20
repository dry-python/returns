from returns.io import IOFailure, IOResult, IOSuccess
from returns.result import Failure, Result, Success


def test_bind():
    """Ensures that bind works."""
    def factory(inner_value: int) -> IOResult[int, str]:
        if inner_value > 0:
            return IOSuccess(inner_value * 2)
        return IOFailure(str(inner_value))

    input_value = 5
    bound: IOResult[int, str] = IOSuccess(input_value)

    assert bound.bind(factory) == factory(input_value)
    assert str(bound.bind(factory)) == '<IOResult: <Success: 10>>'

    input_value = 0
    bound2: IOResult[int, str] = IOSuccess(input_value)

    assert bound2.bind(factory) == factory(input_value)
    assert str(bound2.bind(factory)) == '<IOResult: <Failure: 0>>'


def test_unify_and_bind():
    """Ensures that left identity works for IOSuccess container."""
    def factory(inner_value: int) -> IOResult[int, str]:
        return IOSuccess(inner_value * 2)

    bound: IOResult[int, str] = IOSuccess(5)

    assert bound.unify(factory) == bound.bind(factory)
    assert bound.bind(factory) == bound.unify(factory)


def test_left_identity_success():
    """Ensures that left identity works for IOSuccess container."""
    def factory(inner_value: int) -> IOResult[int, str]:
        return IOSuccess(inner_value * 2)

    input_value = 5
    bound: IOResult[int, str] = IOSuccess(input_value)

    assert bound.bind(factory) == factory(input_value)


def test_left_identity_failure():
    """Ensures that left identity works for IOFailure container."""
    def factory(inner_value: int) -> IOResult[int, int]:
        return IOFailure(6)

    input_value = 5
    bound: IOResult[int, int] = IOFailure(input_value)

    assert bound.bind(factory) == IOFailure(input_value)


def test_bind_regular_result():
    """Ensures that regular ``Result`` can be bound to ``IOResult``."""
    def factory(inner_value: int) -> Result[int, str]:
        if inner_value > 0:
            return Success(inner_value + 1)
        return Failure('nope')

    first: IOResult[int, str] = IOSuccess(1)
    second: IOResult[int, str] = IOSuccess(0)
    third: IOResult[int, str] = IOFailure('a')

    assert first.bind_result(factory) == IOSuccess(2)
    assert second.bind_result(factory) == IOFailure('nope')
    assert third.bind_result(factory) == IOFailure('a')


def test_rescue_success():
    """Ensures that rescue works for IOSuccess container."""
    def factory(inner_value) -> IOResult[int, str]:
        return IOSuccess(inner_value * 2)

    bound = IOSuccess(5).rescue(factory)

    assert bound == IOSuccess(5)


def test_rescue_failure():
    """Ensures that rescue works for IOFailure container."""
    def factory(inner_value: int) -> IOResult[str, int]:
        return IOFailure(inner_value + 1)

    expected = 6
    bound: IOResult[str, int] = IOFailure(5)

    assert bound.rescue(factory) == IOFailure(expected)
