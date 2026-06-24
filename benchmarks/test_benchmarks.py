"""Performance benchmarks for the core ``returns`` containers.

These benchmarks exercise the hot paths of the most commonly used
containers (``Result``, ``Maybe``, ``IO``) together with the pipeline
and iterable helpers. They are measured by CodSpeed in CI.
"""

from returns.io import IO
from returns.iterables import Fold
from returns.maybe import Maybe, Nothing, Some
from returns.pipeline import flow
from returns.pointfree import bind, map_
from returns.result import Failure, Result, Success, safe


def _increment(value: int) -> int:
    return value + 1


def _as_success(value: int) -> Result[int, str]:
    return Success(value + 1)


def _as_some(value: int) -> Maybe[int]:
    return Some(value + 1)


def test_result_map_chain(benchmark) -> None:
    """A long chain of ``.map`` calls over a ``Result``."""

    def run() -> Result[int, str]:
        container: Result[int, str] = Success(0)
        for _ in range(100):
            container = container.map(_increment)
        return container

    assert benchmark(run) == Success(100)


def test_result_bind_chain(benchmark) -> None:
    """A long chain of ``.bind`` calls over a ``Result``."""

    def run() -> Result[int, str]:
        container: Result[int, str] = Success(0)
        for _ in range(100):
            container = container.bind(_as_success)
        return container

    assert benchmark(run) == Success(100)


def test_result_do_notation(benchmark) -> None:
    """Compose ``Result`` values through ``.do`` notation."""

    def run() -> Result[int, str]:
        return Result.do(
            first + second for first in Success(1) for second in Success(2)
        )

    assert benchmark(run) == Success(3)


def test_maybe_do_notation(benchmark) -> None:
    """Compose ``Maybe`` values through ``.do`` notation."""

    def run() -> Maybe[int]:
        return Maybe.do(
            first + second for first in Some(1) for second in Some(2)
        )

    assert benchmark(run) == Some(3)


def test_result_failure_lash(benchmark) -> None:
    """Recover from a failure using ``.lash`` and ``.value_or``."""

    value = 42

    def run() -> int:
        container: Result[int, str] = Failure('boom')
        return container.lash(lambda _: Success(value)).value_or(0)

    assert benchmark(run) == value


def test_safe_decorator(benchmark) -> None:
    """The ``@safe`` decorator wrapping a raising function."""

    @safe
    def _divide(numerator: int, denominator: int) -> float:
        return numerator / denominator

    def run() -> Result[float, Exception]:
        return _divide(10, 0)

    result = benchmark(run)
    assert isinstance(result, Failure)


def test_maybe_map_chain(benchmark) -> None:
    """A long chain of ``.map`` calls over a ``Maybe``."""

    def run() -> Maybe[int]:
        container: Maybe[int] = Some(0)
        for _ in range(100):
            container = container.map(_increment)
        return container

    assert benchmark(run) == Some(100)


def test_maybe_bind_nothing(benchmark) -> None:
    """Short-circuiting a ``Maybe`` chain through ``Nothing``."""

    def run() -> int:
        container: Maybe[int] = Some(1)
        container = container.bind(lambda _: Nothing)
        return container.bind(_as_some).value_or(-1)

    assert benchmark(run) == -1


def test_io_map_chain(benchmark) -> None:
    """A long chain of ``.map`` calls over an ``IO`` container."""

    def run() -> IO[int]:
        container = IO(0)
        for _ in range(100):
            container = container.map(_increment)
        return container

    assert benchmark(run) == IO(100)


def test_flow_pipeline(benchmark) -> None:
    """Compose containers through ``flow`` with point-free helpers."""

    def run() -> Result[int, str]:
        return flow(
            Success(1),
            map_(_increment),
            bind(_as_success),
            map_(_increment),
        )

    assert benchmark(run) == Success(4)


def test_fold_collect_results(benchmark) -> None:
    """Fold an iterable of ``Result`` values into a single container."""
    items = [Success(index) for index in range(100)]

    def run() -> Result[tuple[int, ...], str]:
        return Fold.collect(items, Success(()))

    assert benchmark(run) == Success(tuple(range(100)))
