from typing import List, Tuple

import pytest

from returns.context import NoDeps, ReaderIOResult
from returns.io import IOFailure, IOSuccess
from returns.pipeline import managed
from returns.result import Failure, Result, Success

_aquire_success = ReaderIOResult.from_value('aquire success')
_aquire_failure = ReaderIOResult.from_failure('aquire failure')


def _use_success(inner_value: str) -> ReaderIOResult[NoDeps, str, str]:
    return ReaderIOResult.from_value('use success')


def _use_failure(inner_value: str) -> ReaderIOResult[NoDeps, str, str]:
    return ReaderIOResult.from_failure('use failure')


class _ReleaseSuccess(object):
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderIOResult[NoDeps, None, str]:
        self._logs.append((inner_value, use_result))
        return ReaderIOResult.from_value(None)


class _ReleaseFailure(object):
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderIOResult[NoDeps, None, str]:
        return ReaderIOResult.from_failure('release failure')


@pytest.mark.parametrize(('aquire', 'use', 'release', 'final_result', 'log'), [
    # Aquire success:
    (
        _aquire_success,
        _use_success,
        _ReleaseSuccess,
        IOSuccess('use success'),
        [('aquire success', Success('use success'))],
    ),
    (
        _aquire_success,
        _use_success,
        _ReleaseFailure,
        IOSuccess('use success'),
        [],
    ),
    (
        _aquire_success,
        _use_failure,
        _ReleaseSuccess,
        IOFailure('use failure'),
        [('aquire success', Failure('use failure'))],
    ),
    (
        _aquire_success,
        _use_failure,
        _ReleaseFailure,
        IOFailure('use failure'),
        [],
    ),

    # Aquire failure:
    (
        _aquire_failure,
        _use_success,
        _ReleaseSuccess,
        IOFailure('aquire failure'),
        [],
    ),
    (
        _aquire_failure,
        _use_failure,
        _ReleaseSuccess,
        IOFailure('aquire failure'),
        [],
    ),
    (
        _aquire_failure,
        _use_success,
        _ReleaseFailure,
        IOFailure('aquire failure'),
        [],
    ),
    (
        _aquire_failure,
        _use_failure,
        _ReleaseFailure,
        IOFailure('aquire failure'),
        [],
    ),
])
def test_all_success(aquire, use, release, final_result, log):
    """Ensures that managed works as intended."""
    pipeline_logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(  # type: ignore
        use,
        release(pipeline_logs),
    )(aquire)

    assert pipeline_result(ReaderIOResult.empty) == final_result
    assert pipeline_logs == log


def test_full_typing():
    """This test is here to be a case for typing."""
    logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        _use_success,
        _ReleaseSuccess(logs),
    )(_aquire_success)

    assert pipeline_result(ReaderIOResult.empty) == IOSuccess('use success')
    assert logs == [('aquire success', Success('use success'))]
