# -*- coding: utf-8 -*-

from returns.converters import fold_ioresult, fold_maybe, fold_result
from returns.io import IO, IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


def _success_case(state: int) -> int:
    return state + 1


def _failed_case(_) -> int:
    return 0


_result_converter = fold_result(_success_case, _failed_case)
_maybe_converter = fold_maybe(_success_case, _failed_case)
_ioresult_converter = fold_ioresult(
    IO.lift(_success_case),
    IO.lift(_failed_case),
)


def test_fold_result():
    """Ensures that `fold` is always returning the correct type."""
    assert _result_converter(Success(1)) == 2
    assert _result_converter(Failure(1)) == 0


def test_fold_ioresult():
    """Ensures that `fold` is always returning the correct type."""
    assert _ioresult_converter(IOSuccess(1)) == IO(2)
    assert _ioresult_converter(IOFailure(1)) == IO(0)


def test_fold_maybe():
    """Ensures that `fold` is always returning the correct type."""
    assert _maybe_converter(Some(2)) == 3
    assert _maybe_converter(Nothing) == 0
