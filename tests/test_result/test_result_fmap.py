# -*- coding: utf-8 -*-

from returns.result import Failure, Success


def test_fmap_success():
    """Ensures that Failure identity works for Success monad."""
    assert Success(5).fmap(str) == Success('5')


def test_fmap_failure():
    """Ensures that Failure identity works for Success monad."""
    assert Failure(5).fmap(str) == Failure(5)


def test_efmap_success():
    """Ensures that Failure identity works for Success monad."""
    assert Success(5).efmap(str) == Success(5)


def test_efmap_failure():
    """Ensures that Failure identity works for Success monad."""
    assert Failure(5).efmap(str) == Success('5')
