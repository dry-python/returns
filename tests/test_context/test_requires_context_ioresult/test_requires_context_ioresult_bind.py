from returns.context import RequiresContext
from returns.context import RequiresContextIOResult as RCR  # noqa: N814
from returns.context import RequiresContextResult
from returns.io import IOFailure, IOResult, IOSuccess
from returns.result import Failure, Result, Success


def test_bind():
    """Ensures that bind works."""
    def factory(inner_value: int) -> RCR[int, float, str]:
        if inner_value > 0:
            return RCR(lambda deps: IOSuccess(inner_value / deps))
        return RCR.from_failure(str(inner_value))

    input_value = 5
    bound: RCR[int, int, str] = RCR.from_value(input_value)
    assert bound.bind(factory)(2) == factory(input_value)(2)
    assert bound.bind(factory)(2) == IOSuccess(2.5)

    assert RCR.from_value(0).bind(
        factory,
    )(2) == factory(0)(2) == IOFailure('0')


def test_bind_regular_result():
    """Ensures that regular ``Result`` can be bound."""
    def factory(inner_value: int) -> Result[int, str]:
        if inner_value > 0:
            return Success(inner_value + 1)
        return Failure('nope')

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_result(factory)(RCR.empty) == IOSuccess(2)
    assert RCR.from_value(0).bind_result(
        factory,
    )(RCR.empty) == IOFailure('nope')
    assert third.bind_result(factory)(RCR.empty) == IOFailure('a')


def test_bind_ioresult():
    """Ensures that io ``Result`` can be bound."""
    def factory(inner_value: int) -> IOResult[int, str]:
        if inner_value > 0:
            return IOSuccess(inner_value + 1)
        return IOFailure('nope')

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_ioresult(factory)(RCR.empty) == IOSuccess(2)
    assert RCR.from_value(0).bind_ioresult(
        factory,
    )(RCR.empty) == IOFailure('nope')
    assert third.bind_ioresult(factory)(RCR.empty) == IOFailure('a')


def test_bind_regular_context():
    """Ensures that regular ``RequiresContext`` can be bound."""
    def factory(inner_value: int) -> RequiresContext[int, float]:
        return RequiresContext(lambda deps: inner_value / deps)

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_context(factory)(2) == IOSuccess(0.5)
    assert RCR.from_value(2).bind_context(
        factory,
    )(1) == IOSuccess(2.0)
    assert third.bind_context(factory)(1) == IOFailure('a')


def test_bind_result_context():
    """Ensures that ``RequiresContextResult`` can be bound."""
    def factory(inner_value: int) -> RequiresContextResult[int, float, str]:
        return RequiresContextResult(lambda deps: Success(inner_value / deps))

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_context_result(factory)(2) == IOSuccess(0.5)
    assert RCR.from_value(2).bind_context_result(
        factory,
    )(1) == IOSuccess(2.0)
    assert third.bind_context_result(factory)(1) == IOFailure('a')


def test_rescue_success():
    """Ensures that rescue works for Success container."""
    def factory(inner_value) -> RCR[int, int, str]:
        return RCR.from_value(inner_value * 2)

    assert RCR.from_value(5).rescue(
        factory,
    )(0) == RCR.from_value(5)(0)
    assert RCR.from_failure(5).rescue(
        factory,
    )(0) == RCR.from_value(10)(0)


def test_rescue_failure():
    """Ensures that rescue works for Failure container."""
    def factory(inner_value) -> RCR[int, int, str]:
        return RCR.from_failure(inner_value * 2)

    assert RCR.from_value(5).rescue(
        factory,
    )(0) == RCR.from_value(5)(0)
    assert RCR.from_failure(5).rescue(
        factory,
    )(0) == RCR.from_failure(10)(0)
