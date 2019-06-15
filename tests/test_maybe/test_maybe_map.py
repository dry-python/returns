# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_map_some():
    """Ensures that map works for Some container."""
    assert Some(5).map(str) == Some('5')


def test_map_nothing():
    """Ensures that map works for Nothing container."""
    assert Nothing.map(str) == Nothing


def test_fix_some():
    """Ensures that fix works for Some container."""
    assert Some(5).fix(str) == Some(5)


def test_fix_nothing():
    """Ensures that fix works for Nothing container."""
    assert Nothing.fix(lambda: 2) == Some(2)
