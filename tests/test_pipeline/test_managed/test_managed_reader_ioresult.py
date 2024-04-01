from typing import List, Tuple

import pytest

from returns.context import NoDeps, ReaderIOResult
from returns.io import IOFailure, IOSuccess
from returns.pipeline import managed
from returns.result import Failure, Result, Success

_acquire_success = ReaderIOResult.from_value('acquire success')
_acquire_failure = ReaderIOResult.from_failure('acquire failure')


def _use_success(inner_value: str) -> ReaderIOResult[str, str, NoDeps]:
    return ReaderIOResult.from_value('use success')


def _use_failure(inner_value: str) -> ReaderIOResult[str, str, NoDeps]:
    return ReaderIOResult.from_failure('use failure')


class _ReleaseSuccess:
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderIOResult[None, str, NoDeps]:
        self._logs.append((inner_value, use_result))
        return ReaderIOResult.from_value(None)


class _ReleaseFailure:
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderIOResult[None, str, NoDeps]:
        return ReaderIOResult.from_failure('release failure')


@pytest.mark.parametrize(('acquire', 'use', 'release', 'final_result', 'log'), [
    # Acquire success:
    (
        _acquire_success,
        _use_success,
        _ReleaseSuccess,
        IOSuccess('use success'),
        [('acquire success', Success('use success'))],
    ),
    (
        _acquire_success,
        _use_success,
        _ReleaseFailure,
        IOFailure('release failure'),
        [],
    ),
    (
        _acquire_success,
        _use_failure,
        _ReleaseSuccess,
        IOFailure('use failure'),
        [('acquire success', Failure('use failure'))],
    ),
    (
        _acquire_success,
        _use_failure,
        _ReleaseFailure,
        IOFailure('release failure'),
        [],
    ),

    # Acquire failure:
    (
        _acquire_failure,
        _use_success,
        _ReleaseSuccess,
        IOFailure('acquire failure'),
        [],
    ),
    (
        _acquire_failure,
        _use_failure,
        _ReleaseSuccess,
        IOFailure('acquire failure'),
        [],
    ),
    (
        _acquire_failure,
        _use_success,
        _ReleaseFailure,
        IOFailure('acquire failure'),
        [],
    ),
    (
        _acquire_failure,
        _use_failure,
        _ReleaseFailure,
        IOFailure('acquire failure'),
        [],
    ),
])
def test_all_success(acquire, use, release, final_result, log):
    """Ensures that managed works as intended."""
    pipeline_logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        use,
        release(pipeline_logs),
    )(acquire)

    assert pipeline_result(ReaderIOResult.no_args) == final_result
    assert pipeline_logs == log


def test_full_typing():
    """This test is here to be a case for typing."""
    logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        _use_success,
        _ReleaseSuccess(logs),
    )(_acquire_success)

    assert pipeline_result(ReaderIOResult.no_args) == IOSuccess('use success')
    assert logs == [('acquire success', Success('use success'))]
