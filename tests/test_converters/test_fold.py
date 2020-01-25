# -*- coding: utf-8 -*-

from returns.converters import fold_maybe, fold_result
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


def _success_case(state: int) -> int:
    return state + 1


def _failed_case(_) -> int:
    return 0


_result_converter = fold_result(_success_case, _failed_case)
_maybe_converter = fold_maybe(_success_case, _failed_case)


def test_fold_success():
    """Ensures that `fold` is always returning the correct type."""
    assert _result_converter(Success(1)) == 2


def test_fold_failure():
    """Ensures that `fold` is always returning the correct type."""
    assert _result_converter(Failure(1)) == 0


def test_fold_some():
    """Ensures that `fold` is always returning the correct type."""
    assert _maybe_converter(Some(2)) == 3


def test_fold_nothing():
    """Ensures that `fold` is always returning the correct type."""
    assert _maybe_converter(Nothing) == 0
