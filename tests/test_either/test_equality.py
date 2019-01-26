# -*- coding: utf-8 -*-

from dry_monads.either import Left, Right


def test_nonequality():
    """Ensures that monads are not compared to regular values."""
    input_value = 5

    assert Left(input_value) != input_value
    assert Right(input_value) != input_value
