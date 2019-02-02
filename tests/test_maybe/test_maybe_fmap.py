# -*- coding: utf-8 -*-

from returns.maybe import Nothing, Some


def test_fmap_some():
    """Ensures that fmap works for Some monad."""
    assert Some(5).fmap(str) == Some('5')


def test_fmap_nothing():
    """Ensures that fmap works for Nothing monad."""
    assert Nothing().fmap(str) == Nothing(None)


def test_efmap_some():
    """Ensures that efmap works for Some monad."""
    assert Some(5).efmap(str) == Some(5)


def test_efmap_nothing():
    """Ensures that efmap works for Nothing monad."""
    assert Nothing().efmap(lambda state: str(state)) == Some('None')
