from typing import List, Tuple

import pytest

from returns.context import NoDeps, ReaderFutureResult
from returns.io import IOFailure, IOSuccess
from returns.pipeline import managed
from returns.result import Failure, Result, Success


def _acquire_success() -> ReaderFutureResult[NoDeps, str, str]:
    return ReaderFutureResult.from_value('acquire success')


def _acquire_failure() -> ReaderFutureResult[NoDeps, str, str]:
    return ReaderFutureResult.from_failure('acquire failure')


def _use_success(inner_value: str) -> ReaderFutureResult[NoDeps, str, str]:
    return ReaderFutureResult.from_value('use success')


def _use_failure(inner_value: str) -> ReaderFutureResult[NoDeps, str, str]:
    return ReaderFutureResult.from_failure('use failure')


class _ReleaseSuccess(object):
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderFutureResult[NoDeps, None, str]:
        self._logs.append((inner_value, use_result))
        return ReaderFutureResult.from_value(None)


class _ReleaseFailure(object):
    def __init__(self, logs: List[Tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> ReaderFutureResult[NoDeps, None, str]:
        return ReaderFutureResult.from_failure('release failure')


@pytest.mark.anyio
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
        IOSuccess('use success'),
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
        IOFailure('use failure'),
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
async def test_all_success(acquire, use, release, final_result, log):
    """Ensures that managed works as intended."""
    pipeline_logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(  # type: ignore
        use,
        release(pipeline_logs),
    )(acquire())

    assert await pipeline_result(ReaderFutureResult.empty) == final_result
    assert pipeline_logs == log


@pytest.mark.anyio
async def test_full_typing():
    """This test is here to be a case for typing."""
    logs: List[Tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        _use_success,
        _ReleaseSuccess(logs),
    )(_acquire_success())
    inner = pipeline_result(ReaderFutureResult.empty)

    assert await inner == IOSuccess('use success')
    assert logs == [('acquire success', Success('use success'))]
