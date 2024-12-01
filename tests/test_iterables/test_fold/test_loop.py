import sys
from collections.abc import Iterable
from typing import List, Tuple

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


def _sum_two(first):
    return lambda second: first + second


@pytest.mark.parametrize(('iterable', 'sequence'), [
    # Regular types:

    ([], IO(10)),
    ([IO(1)], IO(11)),
    ([IO(1), IO(2)], IO(13)),

    # Can fail:

    ([], Success(10)),
    ([Success(1)], Success(11)),
    ([Success(1), Success(2)], Success(13)),
    (
        [Failure('a'), Success(1), Success(2)],
        Failure('a'),
    ),
    ([Success(1), Failure('a')], Failure('a')),
    ([Failure('a'), Failure('b')], Failure('a')),

    ([], Some(10)),
    ([Some(1)], Some(11)),
    ([Some(1), Some(2)], Some(13)),
    ([Nothing, Some(1), Some(2)], Nothing),
    ([Some(1), Nothing, Some(2)], Nothing),
    ([Some(1), Some(2), Nothing], Nothing),
    ([Nothing], Nothing),

    ([], IOSuccess(10)),
    ([IOSuccess(1)], IOSuccess(11)),
    ([IOSuccess(1), IOSuccess(2)], IOSuccess(13)),
    (
        [IOFailure('a'), IOSuccess(1), IOSuccess(2)],
        IOFailure('a'),
    ),
    ([IOFailure('a'), IOFailure('b')], IOFailure('a')),
])
def test_fold_loop(iterable, sequence):
    """Iterable for ``Result`` and ``FailFast``."""
    assert Fold.loop(iterable, sequence.from_value(10), _sum_two) == sequence


@pytest.mark.parametrize(('iterable', 'sequence'), [
    # Regular types:

    ([], Reader.from_value(10)),
    ([Reader.from_value(1)], Reader.from_value(11)),
    (
        [Reader.from_value(1), Reader.from_value(2)],
        Reader.from_value(13),
    ),

    # Can fail:

    ([], ReaderResult.from_value(10)),
    ([ReaderResult.from_value(1)], ReaderResult.from_value(11)),
    (
        [ReaderResult.from_value(1), ReaderResult.from_value(2)],
        ReaderResult.from_value(13),
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

    ([], ReaderIOResult.from_value(10)),
    ([ReaderIOResult.from_value(1)], ReaderIOResult.from_value(11)),
    (
        [ReaderIOResult.from_value(1), ReaderIOResult.from_value(2)],
        ReaderIOResult.from_value(13),
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
    (
        [ReaderIOResult.from_value(1), ReaderIOResult.from_failure('a')],
        ReaderIOResult.from_failure('a'),
    ),
])
def test_fold_loop_reader(iterable, sequence):
    """Ensures that ``.loop`` works for readers."""
    assert Fold.loop(
        iterable,
        sequence.from_value(10),
        _sum_two,
    )(...) == sequence(...)


@pytest.mark.anyio
async def test_fold_loop_reader_future_result(subtests):
    """Iterable for ``ReaderFutureResult`` and ``Fold``."""
    containers: list[tuple[  # noqa: WPS234
        Iterable[ReaderFutureResult[int, str, NoDeps]],
        ReaderFutureResult[int, str, NoDeps],
    ]] = [
        ([], ReaderFutureResult.from_value(10)),
        (
            [ReaderFutureResult.from_value(1)],
            ReaderFutureResult.from_value(11),
        ),
        (
            [
                ReaderFutureResult.from_value(1),
                ReaderFutureResult.from_value(2),
            ],
            ReaderFutureResult.from_value(13),
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
        (
            [
                ReaderFutureResult.from_value(1),
                ReaderFutureResult.from_failure('a'),
            ],
            ReaderFutureResult.from_failure('a'),
        ),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Fold.loop(
                iterable, sequence.from_value(10), _sum_two,
            )(...) == await sequence(...)


@pytest.mark.anyio
async def test_fold_collect_future(subtests):
    """Iterable for ``Future`` and ``Fold``."""
    containers: list[tuple[  # noqa: WPS234
        Iterable[Future[int]],
        Future[int],
    ]] = [
        ([], Future.from_value(10)),
        ([Future.from_value(1)], Future.from_value(11)),
        (
            [Future.from_value(1), Future.from_value(2)],
            Future.from_value(13),
        ),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Fold.loop(
                iterable, sequence.from_value(10), _sum_two,
            ) == await sequence


@pytest.mark.anyio
async def test_fold_collect_future_result(subtests):
    """Iterable for ``FutureResult`` and ``Fold``."""
    containers: list[tuple[  # noqa: WPS234
        Iterable[FutureResult[int, str]],
        FutureResult[int, str],
    ]] = [
        ([], FutureSuccess(10)),
        ([FutureSuccess(1)], FutureSuccess(11)),
        ([FutureSuccess(1), FutureSuccess(2)], FutureSuccess(13)),
        (
            [FutureFailure('a'), FutureSuccess(1), FutureSuccess(2)],
            FutureFailure('a'),
        ),
        ([FutureFailure('a'), FutureFailure('b')], FutureFailure('a')),
        ([FutureSuccess(1), FutureFailure('a')], FutureFailure('a')),
    ]
    for iterable, sequence in containers:
        with subtests.test(iterable=iterable, sequence=sequence):
            assert await Fold.loop(
                iterable, sequence.from_value(10), _sum_two,
            ) == await sequence


def test_fold_loop_recursion_limit():
    """Ensures that ``.loop`` method is recursion safe."""
    limit = sys.getrecursionlimit() + 1
    iterable = (IO(1) for _ in range(limit))
    assert Fold.loop(iterable, IO(0), _sum_two) == IO(limit)
