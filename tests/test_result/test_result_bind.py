# -*- coding: utf-8 -*-

from returns.result import Failure, Success


def test_left_identity_success():
    """Ensures that Failure identity works for Success monad."""
    def factory(inner_value: int) -> Success[int]:
        return Success(inner_value * 2)

    input_value = 5
    bound = Success(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == 'Success: 10'


def test_left_identity_failure():
    """Ensures that Failure identity works for Success monad."""
    def factory(inner_value: int) -> Failure[TypeError]:
        return Failure(TypeError())

    input_value = 5
    bound = Failure(input_value).bind(factory)

    assert bound == Failure(input_value)
    assert str(bound) == 'Failure: 5'


def test_ebind_success():
    """Ensures that ebind works for Success monad."""
    def factory(inner_value: int) -> Success[int]:
        return Success(inner_value * 2)

    bound = Success(5).ebind(factory)

    assert bound == Success(5)
    assert str(bound) == 'Success: 5'


def test_ebind_failure():
    """Ensures that ebind works for Success monad."""
    def factory(inner_value: int) -> Failure[float]:
        return Failure(float(inner_value + 1))

    expected = 6.0
    bound = Failure(5).ebind(factory)

    assert bound == Failure(expected)
    assert str(bound) == 'Failure: 6.0'
