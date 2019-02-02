# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_some_value():
    """Ensures that value is fetch correctly from the Some."""
    bound = Some(5).value_or(None)

    assert bound == 5


def test_nothing_value():
    """Ensures that value is fetch correctly from the Nothing."""
    bound = Nothing().value_or(default_value=1)

    assert bound == 1
