# -*- coding: utf-8 -*-

from returns.maybe import Maybe, Nothing, Some


def test_maybe_new_some():
    """Ensures that `new` works for Some monad."""
    assert Maybe.new(5) == Some(5)


def test_maybe_new_nothing():
    """Ensures that `new` works for Nothing monad."""
    assert Maybe.new(None) == Nothing()
