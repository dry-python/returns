import sys
from typing import Iterable, List, Sequence, Tuple

import pytest

from returns.context import (
    NoDeps,
    ReaderFutureResult,
    ReaderIOResult,
    ReaderResult,
)
from returns.future import FutureFailure, FutureResult, FutureSuccess
from returns.io import IOFailure, IOSuccess
from returns.iterables import Fold
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize(('iterable', 'sequence'), [
    ([], Some(())),
    ([Some(1)], Some((1,))),
    ([Some(1), Some(2)], Some((1, 2))),
    ([Nothing, Some(1), Some(2)], Some((1, 2))),
    ([Some(1), Nothing, Some(2)], Some((1, 2))),
    ([Some(1), Some(2), Nothing], Some((1, 2))),
    ([Nothing], Some(())),

    ([], Success(())),
    ([Success(1)], Success((1,))),
    ([Success(1), Success(2)], Success((1, 2))),
    (
        [Failure('a'), Success(1), Success(2)],
        Success((1, 2)),
    ),
    ([Success(1), Failure('b')], Success((1,))),
    ([Failure('a'), Failure('b')], Success(())),

    ([], IOSuccess(())),
    ([IOSuccess(1)], IOSuccess((1,))),
    ([IOSuccess(1), IOSuccess(2)], IOSuccess((1, 2))),
    (
        [IOFailure('a'), IOSuccess(1), IOSuccess(2)],
        IOSuccess((1, 2)),
    ),
    ([IOSuccess(1), IOFailure('b')], IOSuccess((1,))),
    ([IOFailure('a'), IOFailure('b')], IOSuccess(())),
])
def test_collect_all_result(iterable, sequence):
    """Iterable for ``Result`` and ``Fold``."""
    assert Fold.collect_all(iterable, sequence.from_value(())) == sequence


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
        ReaderResult.from_value((1, 2)),
    ),
    (
        [ReaderResult.from_failure('a'), ReaderResult.from_failure('b')],
        ReaderResult.from_value(()),
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
        ReaderIOResult.from_value((1, 2)),
    ),
    (
        [ReaderIOResult.from_failure('a'), ReaderIOResult.from_failure('b')],
        ReaderIOResult.from_value(()),
    ),
])
def test_collect_all_reader_result(iterable, sequence):
    """Iterable for ``ReaderResult`` and ``Fold``."""
    assert Fold.collect_all(
        iterable, sequence.from_value(()),
    )(...) == sequence(...)


@pytest.mark.anyio
async def test_collect_all_reader_future_result(subtests):
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
            ReaderFutureResult.from_value((1, 2)),
        ),
        (
            [
                ReaderFutureResult.from_failure('a'),
                ReaderFutureResult.from_failure('b'),
            ],
            ReaderFutureResult.from_value(()),
        ),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Fold.collect_all(
                iterable, sequence.from_value(()),
            )(...) == await sequence(...)


@pytest.mark.anyio
async def test_collect_all_future_result(subtests):
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
            FutureSuccess((1, 2)),
        ),
        ([FutureFailure('a'), FutureFailure('b')], FutureSuccess(())),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Fold.collect_all(
                iterable, sequence.from_value(()),
            ) == await sequence


def test_fold_collect_recursion_limit():
    """Ensures that ``.collect_all`` method is recurion safe."""
    limit = sys.getrecursionlimit() + 1
    iterable = [Success(1) for _ in range(limit)]
    expected = Success((1,) * limit)
    assert Fold.collect_all(iterable, Success(())) == expected
