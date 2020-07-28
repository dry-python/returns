from returns.maybe import Maybe, Nothing, Some
from typing import Optional


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

def test_bind_optional():
    """Ensures that left identity works for Some container."""
    def factory(inner_value: int) -> Optional[int]:
        return inner_value * 2

    input_value = 5
    bound = Some(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Some: 10>'

def test_bind_optional():
    """Ensures that left identity works for Some container."""
    def factory(inner_value: int) -> Optional[int]:
        return None

    input_value = 5
    bound = Some(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Nothing>'
