from returns.converters import (
    coalesce_ioresult,
    coalesce_maybe,
    coalesce_result,
)
from returns.io import IO, IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


def _success_case(state: int) -> int:
    return state + 1


def _failed_case(_) -> int:
    return 0


def _iosuccess_case(state: IO[int]) -> IO[int]:
    return state


def _iofailed_case(_) -> IO[int]:
    return IO(0)


_result_converter = coalesce_result(_success_case, _failed_case)
_maybe_converter = coalesce_maybe(_success_case, _failed_case)
_ioresult_converter = coalesce_ioresult(_iosuccess_case, _iofailed_case)


def test_coalesce_result():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _result_converter(Success(1)) == 2
    assert _result_converter(Failure(1)) == 0


def test_coalesce_ioresult():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _ioresult_converter(IOSuccess(1)) == IO(1)
    assert _ioresult_converter(IOFailure(1)) == IO(0)


def test_coalesce_maybe():
    """Ensures that `coalesce` is always returning the correct type."""
    assert _maybe_converter(Some(2)) == 3
    assert _maybe_converter(Nothing) == 0
