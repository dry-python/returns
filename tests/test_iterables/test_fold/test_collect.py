import sys
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
from returns.io import IO, IOFailure, IOSuccess
from returns.iterables import Fold
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize(('iterable', 'sequence'), [
    # Regular types:

    ([], IO(())),
    ([IO(1)], IO((1,))),
    ([IO(1), IO(2)], IO((1, 2))),

    # Can fail:

    ([], Success(())),
    ([Success(1)], Success((1,))),
    ([Success(1), Success(2)], Success((1, 2))),
    (
        [Failure('a'), Success(1), Success(2)],
        Failure('a'),
    ),
    ([Success(1), Failure('a')], Failure('a')),
    ([Failure('a'), Failure('b')], Failure('a')),

    ([], Some(())),
    ([Some(1)], Some((1,))),
    ([Some(1), Some(2)], Some((1, 2))),
    ([Nothing, Some(1), Some(2)], Nothing),
    ([Some(1), Nothing, Some(2)], Nothing),
    ([Some(1), Some(2), Nothing], Nothing),
    ([Nothing], Nothing),

    ([], IOSuccess(())),
    ([IOSuccess(1)], IOSuccess((1,))),
    ([IOSuccess(1), IOSuccess(2)], IOSuccess((1, 2))),
    (
        [IOFailure('a'), IOSuccess(1), IOSuccess(2)],
        IOFailure('a'),
    ),
    ([IOSuccess(1), IOFailure('a')], IOFailure('a')),
    ([IOFailure('a'), IOFailure('b')], IOFailure('a')),
])
def test_fold_collect(iterable, sequence):
    """Iterable for regular types and ``Fold``."""
    assert Fold.collect(iterable, sequence.from_value(())) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    # Regular types:

    ([], Reader.from_value(())),
    ([Reader.from_value(1)], Reader.from_value((1,))),
    (
        [Reader.from_value(1), Reader.from_value(2)],
        Reader.from_value((1, 2)),
    ),

    # Can fail:

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
def test_fold_collect_reader(iterable, sequence):
    """Ensures that ``.collect`` works for readers."""
    assert Fold.collect(
        iterable,
        sequence.from_value(()),
    )(...) == sequence(...)


@pytest.mark.anyio
async def test_fold_collect_reader_future_result(subtests):
    """Iterable for ``ReaderFutureResult`` and ``Fold``."""
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
            assert await Fold.collect(
                iterable, sequence.from_value(()),
            )(...) == await sequence(...)


@pytest.mark.anyio
async def test_fold_collect_future(subtests):
    """Iterable for ``Future`` and ``Fold``."""
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
            assert await Fold.collect(
                iterable, sequence.from_value(()),
            ) == await sequence


@pytest.mark.anyio
async def test_fold_collect_future_result(subtests):
    """Iterable for ``FutureResult`` and ``Fold``."""
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
            assert await Fold.collect(
                iterable, sequence.from_value(()),
            ) == await sequence


def test_fold_collect_recursion_limit():
    """Ensures that ``.collect`` method is recurion safe."""
    limit = sys.getrecursionlimit() + 1
    iterable = (IO(1) for _ in range(limit))
    expected = IO((1,) * limit)
    assert Fold.collect(iterable, IO(())) == expected
