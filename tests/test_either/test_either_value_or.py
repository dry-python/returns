# -*- coding: utf-8 -*-

from dry_monads.either import Left, Right


def test_success_value():
    """Ensures that value is fetch correctly from the Success."""
    bound = Right(5).value_or(None)

    assert bound == 5


def test_failure_value():
    """Ensures that value is fetch correctly from the Failure."""
    bound = Left(1).value_or(default_value=None)

    assert bound is None
