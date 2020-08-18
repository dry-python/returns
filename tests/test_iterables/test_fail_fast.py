from typing import Iterable, List, Sequence, Tuple

import pytest

from returns.context import (
    NoDeps,
    Reader,
    ReaderFutureResult,
    ReaderIOResult,
    ReaderResult,
)
from returns.future import Future, FutureFailure, FutureResult, FutureSuccess
from returns.io import IO, IOFailure, IOResult, IOSuccess
from returns.maybe import Maybe, Nothing, Some
from returns.primitives.iterables import FailFast
from returns.result import Failure, Result, Success


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], Success(())),
    ([Success(1)], Success((1,))),
    ([Success(1), Success(2)], Success((1, 2))),
    (
        [Failure('a'), Success(1), Success(2)],
        Failure('a'),
    ),
    ([Failure('a'), Failure('b')], Failure('a')),
])
def test_fail_fast_result(iterable, sequence):
    """Iterable for ``Result`` and ``FailFast``."""
    assert Result.from_iterable(iterable, FailFast) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], Some(())),
    ([Some(1)], Some((1,))),
    ([Some(1), Some(2)], Some((1, 2))),
    ([Nothing, Some(1), Some(2)], Nothing),
    ([Nothing], Nothing),
])
def test_fail_fast_maybe(iterable, sequence):
    """Iterable for ``Maybe`` and ``FailFast``."""
    assert Maybe.from_iterable(iterable, FailFast) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], IO(())),
    ([IO(1)], IO((1,))),
    ([IO(1), IO(2)], IO((1, 2))),
])
def test_fail_fast_io(iterable, sequence):
    """Iterable for ``IO`` and ``FailFast``."""
    assert IO.from_iterable(iterable, FailFast) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], IOSuccess(())),
    ([IOSuccess(1)], IOSuccess((1,))),
    ([IOSuccess(1), IOSuccess(2)], IOSuccess((1, 2))),
    (
        [IOFailure('a'), IOSuccess(1), IOSuccess(2)],
        IOFailure('a'),
    ),
    ([IOFailure('a'), IOFailure('b')], IOFailure('a')),
])
def test_fail_fast_ioresult(iterable, sequence):
    """Iterable for ``IOResult`` and ``FailFast``."""
    assert IOResult.from_iterable(iterable, FailFast) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], Reader.from_value(())),
    ([Reader.from_value(1)], Reader.from_value((1,))),
    (
        [Reader.from_value(1), Reader.from_value(2)],
        Reader.from_value((1, 2)),
    ),
])
def test_fail_fast_reader(iterable, sequence):
    """Iterable for ``Reader`` and ``FailFast``."""
    assert Reader.from_iterable(iterable, FailFast)(...) == sequence(...)


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], ReaderResult.from_value(())),
    ([ReaderResult.from_value(1)], ReaderResult.from_value((1,))),
    (
        [ReaderResult.from_value(1), ReaderResult.from_value(2)],
        ReaderResult.from_value((1, 2)),
    ),
    (
        [
            ReaderResult.from_failure('a'),
            ReaderResult.from_value(1),
            ReaderResult.from_value(2),
        ],
        ReaderResult.from_failure('a'),
    ),
    (
        [ReaderResult.from_failure('a'), ReaderResult.from_failure('b')],
        ReaderResult.from_failure('a'),
    ),
])
def test_fail_fast_reader_result(iterable, sequence):
    """Iterable for ``ReaderResult`` and ``FailFast``."""
    assert ReaderResult.from_iterable(
        iterable, FailFast,
    )(...) == sequence(...)


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], ReaderIOResult.from_value(())),
    ([ReaderIOResult.from_value(1)], ReaderIOResult.from_value((1,))),
    (
        [ReaderIOResult.from_value(1), ReaderIOResult.from_value(2)],
        ReaderIOResult.from_value((1, 2)),
    ),
    (
        [
            ReaderIOResult.from_failure('a'),
            ReaderIOResult.from_value(1),
            ReaderIOResult.from_value(2),
        ],
        ReaderIOResult.from_failure('a'),
    ),
    (
        [ReaderIOResult.from_failure('a'), ReaderIOResult.from_failure('b')],
        ReaderIOResult.from_failure('a'),
    ),
])
def test_fail_fast_reader_ioresult(iterable, sequence):
    """Iterable for ``ReaderIOResult`` and ``FailFast``."""
    assert ReaderIOResult.from_iterable(
        iterable, FailFast,
    )(...) == sequence(...)


@pytest.mark.anyio
async def test_fail_fast_reader_future_result(subtests):
    """Iterable for ``ReaderFutureResult`` and ``FailFast``."""
    containers: List[Tuple[  # noqa: WPS234
        Iterable[ReaderFutureResult[int, str, NoDeps]],
        ReaderFutureResult[Sequence[int], str, NoDeps],
    ]] = [
        ([], ReaderFutureResult.from_value(())),
        (
            [ReaderFutureResult.from_value(1)],
            ReaderFutureResult.from_value((1,)),
        ),
        (
            [
                ReaderFutureResult.from_value(1),
                ReaderFutureResult.from_value(2),
            ],
            ReaderFutureResult.from_value((1, 2)),
        ),
        (
            [
                ReaderFutureResult.from_failure('a'),
                ReaderFutureResult.from_value(1),
                ReaderFutureResult.from_value(2),
            ],
            ReaderFutureResult.from_failure('a'),
        ),
        (
            [
                ReaderFutureResult.from_failure('a'),
                ReaderFutureResult.from_failure('b'),
            ],
            ReaderFutureResult.from_failure('a'),
        ),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await ReaderFutureResult.from_iterable(
                iterable, FailFast,
            )(...) == await sequence(...)


@pytest.mark.anyio
async def test_fail_fast_future(subtests):
    """Iterable for ``Future`` and ``FailFast``."""
    containers: List[Tuple[  # noqa: WPS234
        Iterable[Future[int]],
        Future[Sequence[int]],
    ]] = [
        ([], Future.from_value(())),
        ([Future.from_value(1)], Future.from_value((1,))),
        (
            [Future.from_value(1), Future.from_value(2)],
            Future.from_value((1, 2)),
        ),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Future.from_iterable(
                iterable, FailFast,
            ) == await sequence


@pytest.mark.anyio
async def test_fail_fast_future_result(subtests):
    """Iterable for ``FutureResult`` and ``FailFast``."""
    containers: List[Tuple[  # noqa: WPS234
        Iterable[FutureResult[int, str]],
        FutureResult[Sequence[int], str],
    ]] = [
        ([], FutureSuccess(())),
        ([FutureSuccess(1)], FutureSuccess((1,))),
        ([FutureSuccess(1), FutureSuccess(2)], FutureSuccess((1, 2))),
        (
            [FutureFailure('a'), FutureSuccess(1), FutureSuccess(2)],
            FutureFailure('a'),
        ),
        ([FutureFailure('a'), FutureFailure('b')], FutureFailure('a')),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await FutureResult.from_iterable(
                iterable, FailFast,
            ) == await sequence
