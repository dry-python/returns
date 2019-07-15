# -*- coding: utf-8 -*-

from returns.maybe import Maybe, Nothing, Some


def test_bind_some():
    """Ensures that left identity works for Some container."""
    def factory(inner_value: int) -> Maybe[int]:
        return Some(inner_value * 2)

    input_value = 5
    bound = Some(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Some: 10>'


def test_bind_nothing():
    """Ensures that left identity works for Nothing container."""
    def factory(inner_value) -> Maybe[int]:
        return Some(1)

    bound = Nothing.bind(factory)

    assert bound == Nothing
    assert str(bound) == '<Nothing>'


def test_rescue_some():
    """Ensures that rescue works for Some container."""
    def factory() -> Maybe[int]:
        return Some(10)

    bound = Some(5).rescue(factory)

    assert bound == Some(5)


def test_rescue_nothing():
    """Ensures that rescue works for Nothing container."""
    def factory() -> Maybe[int]:
        return Some(1)

    bound = Nothing.rescue(factory)
    bound2 = Nothing.rescue(lambda _: Some(1))

    assert bound == bound2
