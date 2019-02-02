# -*- coding: utf-8 -*-

from returns.either import Either, Failure, Left, Result, Right, Success


def test_aliases():
    """Ensures that aliases are correct."""
    assert Right is Success
    assert Left is Failure
    assert Either is Result
