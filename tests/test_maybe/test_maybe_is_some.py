# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_is_some_on_some():
    """Ensures that Some check returns ``True`` for Some container."""
    assert Some(5).is_some()


def test_is_some_on_nothing():
    """Ensures that Some check returns ``False`` for Nothing container."""
    assert not Nothing.is_some()
