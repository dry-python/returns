# -*- coding: utf-8 -*-

from returns.converters import coalesce_maybe, coalesce_result
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


def _success_case(state: int) -> int:
    return state + 1


def _failed_case(_) -> int:
    return 0


_result_converter = coalesce_result(_success_case, _failed_case)
_maybe_converter = coalesce_maybe(_success_case, _failed_case)


def test_coalesce_success():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _result_converter(Success(1)) == 2


def test_coalesce_failure():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _result_converter(Failure(1)) == 0


def test_coalesce_some():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _maybe_converter(Some(2)) == 3


def test_coalesce_nothing():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _maybe_converter(Nothing) == 0
