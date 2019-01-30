# -*- coding: utf-8 -*-

from dry_monads.either import Left, Right


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
