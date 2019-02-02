# -*- coding: utf-8 -*-

from returns.functions import safe
from returns.result import Failure, Success


@safe
def _function(number: int) -> float:
    return number / number


def test_safe_success():
    """Ensures that safe decorator works correctly for success case."""
    assert _function(1) == Success(1)


def test_safe_failure():
    """Ensures that safe decorator works correctly for failure case."""
    assert isinstance(_function(0), Failure)
