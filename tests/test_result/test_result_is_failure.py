# -*- coding: utf-8 -*-

from returns.result import Failure, Success


def test_is_failure_on_success():
    """Ensures that Failure check returns ``False`` for Success container."""
    assert not Success(5).is_failure()


def test_is_failure_on_failure():
    """Ensures that Failure check returns ``True`` for Failure container."""
    assert Failure(5).is_failure()
