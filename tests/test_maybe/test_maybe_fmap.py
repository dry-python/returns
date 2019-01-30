# -*- coding: utf-8 -*-

from dry_monads.maybe import Nothing, Some


def test_fmap_some():
    """Ensures that fmap works for Some monad."""
    assert Some(5).fmap(str) == Some('5')


def test_fmap_nothing():
    """Ensures that fmap works for Nothing monad."""
    assert Nothing().fmap(str) == Nothing(None)
