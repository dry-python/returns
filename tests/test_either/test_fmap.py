# -*- coding: utf-8 -*-

from dry_monads.either import Left, Right


def test_fmap_success():
    """Ensures that left identity works for Right monad."""
    assert Right(5).fmap(str) == Right('5')


def test_fmap_failure():
    """Ensures that left identity works for Right monad."""
    assert Left(5).fmap(str) == Left(5)
