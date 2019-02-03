# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_bind_some():
    """Ensures that Failure identity works for Some monad."""
    def factory(inner_value: int) -> Some[int]:
        return Some(inner_value * 2)

    input_value = 5
    bound = Some(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == 'Some: 10'


def test_bind_nothing():
    """Ensures that Failure identity works for Some monad."""
    def factory(inner_value: None) -> Some[int]:
        return Some(1)

    bound = Nothing().bind(factory)

    assert bound == Nothing(None)
    assert str(bound) == 'Nothing: None'


def test_rescue_some():
    """Ensures that Failure identity works for Some monad."""
    def factory(inner_value: int) -> Some[int]:
        return Some(inner_value * 2)

    bound = Some(5).rescue(factory)

    assert bound == Some(5)
    assert str(bound) == 'Some: 5'


def test_rescue_nothing():
    """Ensures that Failure identity works for Some monad."""
    def factory(inner_value: None) -> Some[int]:
        return Some(1)

    bound = Nothing().rescue(factory)

    assert bound == Some(1)
    assert str(bound) == 'Some: 1'
