# -*- coding: utf-8 -*-

from returns.result import Failure, Success


def test_is_success_on_success():
    """Ensures that Success check returns ``True`` for Success container."""
    assert Success(5).is_success()


def test_is_success_on_failure():
    """Ensures that Success check returns ``False`` for Failure container."""
    assert not Failure(5).is_success()
