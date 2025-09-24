from collections.abc import Callable, Sequence
from typing import Any, TypeVar

import pytest
from hypothesis import given
from hypothesis import strategies as st

from returns.context import (
    Reader,
    RequiresContext,
    RequiresContextFutureResult,
    RequiresContextFutureResultE,
    RequiresContextIOResult,
    RequiresContextIOResultE,
    RequiresContextResult,
    RequiresContextResultE,
)
from returns.contrib.hypothesis.laws import (
    Settings,
    _types_to_strategies,  # noqa: PLC2701
    default_settings,
)
from returns.contrib.hypothesis.type_resolver import (
    StrategyFactory,
    apply_strategy,
    look_up_strategy,
)
from returns.future import Future, FutureResult
from returns.interfaces.applicative import ApplicativeN
from returns.io import IO, IOResult, IOResultE
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.primitives.laws import Lawful
from returns.result import Result, ResultE
from test_hypothesis.test_laws import test_custom_type_applicative

_all_containers: Sequence[type[Lawful]] = (
    Maybe,
    Result,
    IO,
    IOResult,
    Future,
    FutureResult,
    RequiresContext,
    RequiresContextResult,
    RequiresContextIOResult,
    RequiresContextFutureResult,
    # Aliases:
    ResultE,
    IOResultE,
    Reader,
    RequiresContextResultE,
    RequiresContextIOResultE,
    RequiresContextFutureResultE,
)


@pytest.mark.filterwarnings('ignore:.*')
@pytest.mark.parametrize('container_type', _all_containers)
def test_all_containers_resolves(container_type: type[Lawful]) -> None:
    """Ensures all containers do resolve."""
    assert st.from_type(container_type).example() is not None


@given(
    st.from_type(ResultE).filter(
        lambda container: not is_successful(container),
    ),
)
def test_result_error_alias_resolves(thing: ResultE[Any]) -> None:
    """Ensures that type aliases are resolved correctly."""
    assert isinstance(thing.failure(), Exception)


CustomResult = Result[int, str]


@given(st.from_type(CustomResult))
def test_custom_result_error_types_resolve(thing: CustomResult) -> None:
    """Ensures that type aliases are resolved correctly."""
    if is_successful(thing):
        assert isinstance(thing.unwrap(), int)
    else:
        assert isinstance(thing.failure(), str)


@given(
    st.from_type(RequiresContextResultE).filter(
        lambda container: not is_successful(
            container(RequiresContextResultE.no_args),
        ),
    ),
)
def test_reader_result_error_alias_resolves(
    thing: RequiresContextResultE,
) -> None:
    """Ensures that type aliases are resolved correctly."""
    real_result = thing(RequiresContextResultE.no_args)
    assert isinstance(real_result.failure(), Exception)


CustomReaderResult = RequiresContextResult[int, str, bool]


@given(st.from_type(CustomReaderResult))
def test_custom_readerresult_types_resolve(
    thing: CustomReaderResult,
) -> None:
    """Ensures that type aliases are resolved correctly."""
    real_result = thing(RequiresContextResultE.no_args)
    if is_successful(real_result):
        assert isinstance(real_result.unwrap(), int)
    else:
        assert isinstance(real_result.failure(), str)


def test_merge_settings() -> None:
    """Check that each part of the settings can be overridden by users."""
    settings1 = Settings(
        settings_kwargs={'a': 1, 'b': 2},
        use_init=False,
        container_strategy=st.integers(),
        type_strategies={int: st.integers(max_value=10), str: st.text('abc')},
    )
    settings2 = Settings(
        settings_kwargs={'a': 1, 'c': 3},
        use_init=False,
        container_strategy=st.integers(max_value=20),
        type_strategies={int: st.integers(max_value=30), bool: st.booleans()},
    )

    result = settings1 | settings2

    assert result == Settings(
        settings_kwargs={'a': 1, 'b': 2, 'c': 3},
        use_init=False,
        container_strategy=st.integers(max_value=20),
        type_strategies={
            int: st.integers(max_value=30),
            bool: st.booleans(),
            str: st.text('abc'),
        },
    )


def test_merge_use_init() -> None:
    """Check that `use_init` can be set to `True` by users.

    Note: They can't set a `True` to `False`, since we use `|` to merge.
    However, the default value is `False`, so this should not be a problem.
    """
    settings1 = Settings(
        settings_kwargs={},
        use_init=False,
        container_strategy=None,
        type_strategies={},
    )
    settings2 = Settings(
        settings_kwargs={},
        use_init=True,
        container_strategy=None,
        type_strategies={},
    )

    result = settings1 | settings2

    assert result == Settings(
        settings_kwargs={},
        use_init=True,
        container_strategy=None,
        type_strategies={},
    )


_ValueType = TypeVar('_ValueType')


def test_types_to_strategies_default() -> None:  # noqa: WPS210
    """Check the default strategies for types."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001
    # NOTE: There is a type error because `Callable` is a
    # special form, not a type.
    callable_type: type[object] = Callable  # type: ignore[assignment]

    result = _types_to_strategies(
        container_type,
        default_settings(container_type),
    )

    wrapper_strategy = (
        'builds(from_value, shared(sampled_from([NoneType,'
        ' bool, int, float, str,'
        " bytes]), key='typevar=~_FirstType').flatmap(from_type))"
    )
    assert (
        _strategy_string(result[container_type], container_type)
        == wrapper_strategy
    )
    assert _strategy_strings(
        [result[interface] for interface in container_type.laws()],
        container_type,
    ) == [
        wrapper_strategy,
        wrapper_strategy,
    ]
    assert (
        _strategy_string(result[callable_type], Callable[[int, str], bool])
        == 'functions(like=lambda *args, **kwargs: None,'
        ' returns=booleans(), pure=True)'
    )
    assert (
        _strategy_string(result[callable_type], Callable[[], None])
        == 'functions(like=lambda: None, returns=none(), pure=True)'
    )
    assert (
        _strategy_string(result[TypeVar], _ValueType)
        == 'shared(sampled_from([NoneType, bool,'
        ' int, float, str, bytes]),'
        " key='typevar=~_ValueType').flatmap(from_type).filter(lambda"
        ' inner: inner == inner)'
    )


def test_types_to_strategies_overrides() -> None:  # noqa: WPS210
    """Check that we allow the user to override all strategies."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001
    # NOTE: There is a type error because `Callable` is a
    # special form, not a type.
    callable_type: type[object] = Callable  # type: ignore[assignment]

    result = _types_to_strategies(
        container_type,
        Settings(
            settings_kwargs={},
            use_init=False,
            container_strategy=st.builds(container_type, st.integers()),
            type_strategies={
                TypeVar: st.text(),
                callable_type: st.functions(returns=st.booleans()),
                # This strategy does not get used, because we use
                # the given `container_strategy` for all interfaces of the
                # container type.
                ApplicativeN: st.tuples(st.integers()),
            },
        ),
    )

    wrapper_strategy = 'builds(_Wrapper, integers())'
    assert (
        _strategy_string(result[container_type], container_type)
        == wrapper_strategy
    )
    assert _strategy_strings(
        [result[interface] for interface in container_type.laws()],
        container_type,
    ) == [
        wrapper_strategy,
        wrapper_strategy,
    ]
    assert (
        _strategy_string(result[callable_type], Callable[[int, str], bool])
        == 'functions(returns=booleans())'
    )
    assert (
        _strategy_string(result[callable_type], Callable[[], None])
        == 'functions(returns=booleans())'
    )
    assert _strategy_string(result[TypeVar], _ValueType) == 'text()'


def _interface_factories(type_: type[Lawful]) -> list[StrategyFactory | None]:
    return [look_up_strategy(interface) for interface in type_.laws()]


def _strategy_strings(
    strategy_factories: Sequence[StrategyFactory | None], type_: type[object]
) -> list[str]:
    return [
        _strategy_string(strategy_factory, type_)
        for strategy_factory in strategy_factories
    ]


def _strategy_string(
    strategy_factory: StrategyFactory | None, type_: Any
) -> str:
    """Return an easily testable string representation."""
    return (
        str(None)
        if strategy_factory is None
        else str(apply_strategy(strategy_factory, type_))
    )
