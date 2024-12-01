
import pytest

from returns.future import FutureResult
from returns.io import IOFailure, IOSuccess
from returns.pipeline import managed
from returns.result import Failure, Result, Success


def _acquire_success() -> FutureResult[str, str]:
    return FutureResult.from_value('acquire success')


def _acquire_failure() -> FutureResult[str, str]:
    return FutureResult.from_failure('acquire failure')


def _use_success(inner_value: str) -> FutureResult[str, str]:
    return FutureResult.from_value('use success')


def _use_failure(inner_value: str) -> FutureResult[str, str]:
    return FutureResult.from_failure('use failure')


class _ReleaseSuccess:
    def __init__(self, logs: list[tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> FutureResult[None, str]:
        self._logs.append((inner_value, use_result))
        return FutureResult.from_value(None)


class _ReleaseFailure:
    def __init__(self, logs: list[tuple[str, Result[str, str]]]) -> None:
        self._logs = logs

    def __call__(
        self,
        inner_value: str,
        use_result: Result[str, str],
    ) -> FutureResult[None, str]:
        return FutureResult.from_failure('release failure')


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
async def test_all_success(acquire, use, release, final_result, log):
    """Ensures that managed works as intended."""
    pipeline_logs: list[tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        use,
        release(pipeline_logs),
    )(acquire())

    assert await pipeline_result == final_result
    assert pipeline_logs == log


@pytest.mark.anyio
async def test_full_typing():
    """This test is here to be a case for typing."""
    logs: list[tuple[str, Result[str, str]]] = []
    pipeline_result = managed(
        _use_success,
        _ReleaseSuccess(logs),
    )(_acquire_success())

    assert await pipeline_result == IOSuccess('use success')
    assert logs == [('acquire success', Success('use success'))]
