# -*- coding: utf-8 -*-

from dry_monads.maybe import Nothing, Some


def test_bind_some():
    """Ensures that Nothing identity works for Some monad."""
    def factory(inner_value: int) -> Some[int]:
        return Some(inner_value * 2)

    input_value = 5
    bound = Some(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == 'Some: 10'


def test_bind_nothing():
    """Ensures that Nothing identity works for Some monad."""
    def factory(inner_value: None) -> Some[int]:
        return Some(1)

    bound = Nothing().bind(factory)

    assert bound == Nothing(None)
    assert str(bound) == 'Nothing: None'
