from returns.context import RequiresContext
from returns.context import RequiresContextResult as RCR  # noqa: N814
from returns.result import Failure, Result, Success


def test_bind():
    """Ensures that bind works."""
    def factory(inner_value: int) -> RCR[int, float, str]:
        if inner_value > 0:
            return RCR(lambda deps: Success(inner_value / deps))
        return RCR.from_failure(str(inner_value))

    input_value = 5
    bound: RCR[int, int, str] = RCR.from_value(input_value)
    assert bound.bind(factory)(2) == factory(input_value)(2)
    assert bound.bind(factory)(2) == Success(2.5)

    assert RCR.from_value(0).bind(
        factory,
    )(2) == factory(0)(2) == Failure('0')


def test_bind_regular_result():
    """Ensures that regular ``Result`` can be bound."""
    def factory(inner_value: int) -> Result[int, str]:
        if inner_value > 0:
            return Success(inner_value + 1)
        return Failure('nope')

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_result(factory)(RCR.empty) == Success(2)
    assert RCR.from_value(0).bind_result(
        factory,
    )(RCR.empty) == Failure('nope')
    assert third.bind_result(factory)(RCR.empty) == Failure('a')


def test_bind_regular_context():
    """Ensures that regular ``RequiresContext`` can be bound."""
    def factory(inner_value: int) -> RequiresContext[int, float]:
        return RequiresContext(lambda deps: inner_value / deps)

    first: RCR[int, int, str] = RCR.from_value(1)
    third: RCR[int, int, str] = RCR.from_failure('a')

    assert first.bind_context(factory)(2) == Success(0.5)
    assert RCR.from_value(2).bind_context(
        factory,
    )(1) == Success(2.0)
    assert third.bind_context(factory)(1) == Failure('a')


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
