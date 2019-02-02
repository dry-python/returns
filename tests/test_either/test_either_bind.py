# -*- coding: utf-8 -*-

from returns.either import Left, Right


def test_left_identity_success():
    """Ensures that left identity works for Right monad."""
    def factory(inner_value: int) -> Right[int]:
        return Right(inner_value * 2)

    input_value = 5
    bound = Right(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == 'Right: 10'


def test_left_identity_failure():
    """Ensures that left identity works for Right monad."""
    def factory(inner_value: int) -> Left[TypeError]:
        return Left(TypeError())

    input_value = 5
    bound = Left(input_value).bind(factory)

    assert bound == Left(input_value)
    assert str(bound) == 'Left: 5'


def test_ebind_success():
    """Ensures that ebind works for Right monad."""
    def factory(inner_value: int) -> Right[int]:
        return Right(inner_value * 2)

    bound = Right(5).ebind(factory)

    assert bound == Right(5)
    assert str(bound) == 'Right: 5'


def test_ebind_failure():
    """Ensures that ebind works for Right monad."""
    def factory(inner_value: int) -> Left[float]:
        return Left(float(inner_value + 1))

    expected = 6.0
    bound = Left(5).ebind(factory)

    assert bound == Left(expected)
    assert str(bound) == 'Left: 6.0'
