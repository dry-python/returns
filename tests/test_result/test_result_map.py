# -*- coding: utf-8 -*-

from returns.result import Failure, Success


def test_map_success():
    """Ensures that Failure identity works for Success monad."""
    assert Success(5).map(str) == Success('5')


def test_map_failure():
    """Ensures that Failure identity works for Success monad."""
    assert Failure(5).map(str) == Failure(5)


def test_fix_success():
    """Ensures that Failure identity works for Success monad."""
    assert Success(5).fix(str) == Success(5)


def test_fix_failure():
    """Ensures that Failure identity works for Success monad."""
    assert Failure(5).fix(str) == Success('5')
