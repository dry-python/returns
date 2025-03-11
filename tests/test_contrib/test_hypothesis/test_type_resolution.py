from collections.abc import Callable, Sequence
from contextlib import ExitStack
from typing import Any, Final, TypeVar

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
    _enter_hypothesis_context,  # noqa: PLC2701
    _Settings,  # noqa: PLC2701
    interface_strategies,
    register_container,
)
from returns.contrib.hypothesis.type_resolver import (
    StrategyFactory,
    apply_strategy,
    look_up_strategy,
    strategies_for_types,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOResult, IOResultE
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.primitives.laws import Lawful
from returns.result import Result, ResultE, Success
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


DEFAULT_RESULT_STRATEGY: Final = (
    "one_of(builds(from_value, shared(sampled_from([<class 'NoneType'>, "
    "<class 'bool'>, <class 'int'>, <class 'float'>, <class 'str'>, "
    "<class 'bytes'>]), key='typevar=~_FirstType').flatmap(from_type)), "
    "builds(from_failure, shared(sampled_from([<class 'NoneType'>, "
    "<class 'bool'>, <class 'int'>, <class 'float'>, <class 'str'>, "
    "<class 'bytes'>]), "
    "key='typevar=~_SecondType').flatmap(from_type)))"
)


def test_register_container_with_no_strategy() -> None:
    """Check that a container without a strategy gets a strategy."""
    container_type = Result

    with register_container(
        container_type,
        settings=_Settings(
            settings_kwargs={}, use_init=False, container_strategy=None
        ),
    ):
        strategy_factory = look_up_strategy(container_type)

    assert (
        _strategy_string(strategy_factory, container_type)
        == DEFAULT_RESULT_STRATEGY
    )


def test_register_container_with_strategy() -> None:
    """Check that when a container has an existing strategy, we drop it."""
    container_type = Result

    with (
        strategies_for_types({
            container_type: st.builds(container_type, st.integers())
        }),
        register_container(
            container_type,
            settings=_Settings(
                settings_kwargs={}, use_init=False, container_strategy=None
            ),
        ),
    ):
        strategy_factory = look_up_strategy(container_type)

    assert (
        _strategy_string(strategy_factory, container_type)
        == DEFAULT_RESULT_STRATEGY
    )


def test_register_container_with_setting() -> None:
    """Check that we prefer a strategy given in settings."""
    container_type = Result

    with register_container(
        container_type,
        settings=_Settings(
            settings_kwargs={},
            use_init=False,
            container_strategy=st.builds(Success, st.integers()),
        ),
    ):
        strategy_factory = look_up_strategy(container_type)

    assert (
        _strategy_string(strategy_factory, container_type)
        == 'builds(Success, integers())'
    )


_ValueType = TypeVar('_ValueType')


def test_hypothesis_state_outside_context() -> None:  # noqa: WPS210
    """Check values of strategies before we register them.

    This is mostly useful as a baseline to compare the the values when we do
    register them.
    """
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001
    # NOTE: There is a type error because `Callable` is a
    # special form, not a type.
    callable_type: type[object] = Callable  # type: ignore[assignment]

    container_strategy_outside = look_up_strategy(container_type)
    interface_strategies_outside = _interface_factories(container_type)
    pure_functions_strategy_outside = look_up_strategy(callable_type)
    type_var_strategy_outside = look_up_strategy(TypeVar)

    assert (
        _strategy_string(container_strategy_outside, container_type) == 'None'
    )
    assert _strategy_strings(interface_strategies_outside, container_type) == [
        'None',
        'None',
    ]
    assert (
        _strategy_string(
            pure_functions_strategy_outside, Callable[[int, str], bool]
        )
        == 'functions(like=lambda *a, **k: None, returns=booleans())'
    )
    assert (
        _strategy_string(type_var_strategy_outside, _ValueType)
        == "shared(sampled_from([<class 'NoneType'>, <class 'bool'>,"
        " <class 'int'>, <class 'float'>, <class 'str'>, <class 'bytes'>]),"
        " key='typevar=~_ValueType').flatmap(from_type)"
    )


def test_hypothesis_state_inside_context() -> None:  # noqa: WPS210
    """Check that strategies are registered correctly."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001
    # NOTE: There is a type error because `Callable` is a
    # special form, not a type.
    callable_type: type[object] = Callable  # type: ignore[assignment]

    with ExitStack() as stack:
        _enter_hypothesis_context(
            stack,
            container_type,
            settings=_Settings(
                settings_kwargs={}, use_init=False, container_strategy=None
            ),
        )
        container_strategy = look_up_strategy(container_type)
        interface_strategies = _interface_factories(container_type)
        pure_functions_strategy = look_up_strategy(callable_type)
        type_var_strategy = look_up_strategy(TypeVar)

    wrapper_strategy = (
        "builds(from_value, shared(sampled_from([<class 'NoneType'>,"
        " <class 'bool'>, <class 'int'>, <class 'float'>, <class 'str'>,"
        " <class 'bytes'>]), key='typevar=~_FirstType').flatmap(from_type))"
    )
    assert (
        _strategy_string(container_strategy, container_type) == wrapper_strategy
    )
    assert _strategy_strings(interface_strategies, container_type) == [
        wrapper_strategy,
        wrapper_strategy,
    ]
    assert (
        _strategy_string(pure_functions_strategy, Callable[[int, str], bool])
        == 'functions(like=lambda *args, **kwargs: <unknown>,'
        ' returns=booleans(), pure=True)'
    )
    assert (
        _strategy_string(pure_functions_strategy, Callable[[], None])
        == 'functions(like=lambda: None, returns=none(), pure=True)'
    )
    assert (
        _strategy_string(type_var_strategy, _ValueType)
        == "shared(sampled_from([<class 'NoneType'>, <class 'bool'>,"
        " <class 'int'>, <class 'float'>, <class 'str'>, <class 'bytes'>]),"
        " key='typevar=~_ValueType').flatmap(from_type).filter(lambda"
        ' inner: inner == inner)'
    )


def test_hypothesis_state_with_setting() -> None:  # noqa: WPS210
    """Check that we prefer the strategies in settings."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001
    # NOTE: There is a type error because `Callable` is a
    # special form, not a type.
    callable_type: type[object] = Callable  # type: ignore[assignment]

    with ExitStack() as stack:
        _enter_hypothesis_context(
            stack,
            container_type,
            settings=_Settings(
                settings_kwargs={},
                use_init=False,
                container_strategy=st.builds(container_type, st.integers()),
            ),
        )
        container_strategy = look_up_strategy(container_type)
        interface_strategies = _interface_factories(container_type)
        pure_functions_strategy = look_up_strategy(callable_type)
        type_var_strategy = look_up_strategy(TypeVar)

    wrapper_strategy = 'builds(_Wrapper, integers())'
    assert (
        _strategy_string(container_strategy, container_type) == wrapper_strategy
    )
    assert _strategy_strings(interface_strategies, container_type) == [
        wrapper_strategy,
        wrapper_strategy,
    ]
    assert (
        _strategy_string(pure_functions_strategy, Callable[[int, str], bool])
        == 'functions(like=lambda *args, **kwargs: <unknown>,'
        ' returns=booleans(), pure=True)'
    )
    assert (
        _strategy_string(pure_functions_strategy, Callable[[], None])
        == 'functions(like=lambda: None, returns=none(), pure=True)'
    )
    assert (
        _strategy_string(type_var_strategy, _ValueType)
        == "shared(sampled_from([<class 'NoneType'>, <class 'bool'>,"
        " <class 'int'>, <class 'float'>, <class 'str'>, <class 'bytes'>]),"
        " key='typevar=~_ValueType').flatmap(from_type).filter(lambda"
        ' inner: inner == inner)'
    )


def test_interface_strategies() -> None:
    """Check that ancestor interfaces get resolved to the concrete container."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001

    with interface_strategies(
        container_type,
        settings=_Settings(
            settings_kwargs={}, use_init=False, container_strategy=None
        ),
    ):
        strategy_factories_inside = _interface_factories(container_type)

    assert _strategy_strings(strategy_factories_inside, container_type) == [
        "builds(from_value, shared(sampled_from([<class 'NoneType'>,"
        " <class 'bool'>, <class 'int'>, <class 'float'>, <class 'str'>,"
        " <class 'bytes'>]), key='typevar=~_FirstType').flatmap(from_type))",
        "builds(from_value, shared(sampled_from([<class 'NoneType'>,"
        " <class 'bool'>, <class 'int'>, <class 'float'>, <class 'str'>,"
        " <class 'bytes'>]), key='typevar=~_FirstType').flatmap(from_type))",
    ]


def test_interface_strategies_with_settings() -> None:
    """Check that we prefer the strategy in the settings."""
    container_type = test_custom_type_applicative._Wrapper  # noqa: SLF001

    with interface_strategies(
        container_type,
        settings=_Settings(
            settings_kwargs={},
            use_init=False,
            container_strategy=st.builds(container_type, st.integers()),
        ),
    ):
        strategy_factories_inside = _interface_factories(container_type)

    assert _strategy_strings(strategy_factories_inside, container_type) == [
        'builds(_Wrapper, integers())',
        'builds(_Wrapper, integers())',
    ]


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
