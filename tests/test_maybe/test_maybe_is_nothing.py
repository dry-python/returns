# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_is_nothing_on_some():
    """Ensures that Nothing check returns ``False`` for Some container."""
    assert not Some(5).is_nothing()


def test_is_nothing_on_nothing():
    """Ensures that Nothing check returns ``True`` for Nothing container."""
    assert Nothing.is_nothing()
