import dataclasses
import inspect
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from typing import Any, TypeVar, final, overload

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from hypothesis.strategies._internal import types  # noqa: PLC2701
from typing_extensions import Self

from returns.contrib.hypothesis.containers import strategy_from_container
from returns.contrib.hypothesis.type_resolver import (
    StrategyFactory,
    strategies_for_types,
)
from returns.primitives.laws import Law, Lawful

Example_co = TypeVar('Example_co', covariant=True)


@final
@dataclasses.dataclass(frozen=True)
class _Settings:
    """Settings that we provide to an end user."""

    settings_kwargs: dict[str, Any]
    use_init: bool
    container_strategy: StrategyFactory | None
    other_strategies: dict[type[object], StrategyFactory] = dataclasses.field(
        default_factory=dict
    )

    def __or__(self, other: Self) -> Self:
        return _Settings(
            settings_kwargs=self.settings_kwargs | other.settings_kwargs,
            use_init=self.use_init | other.use_init,
            container_strategy=self.container_strategy
            if other.container_strategy is None
            else other.container_strategy,
            other_strategies=self.other_strategies | other.other_strategies,
        )

    def __post_init__(self) -> None:
        """Check that the settings are mutually compatible."""
        if self.use_init and self.container_strategy is not None:
            raise AssertionError(
                'Expected only one of `use_init` and'
                ' `container_strategy` to be truthy'
            )


def _default_settings(container_type: type[Lawful]) -> _Settings:
    """Return default settings for creating law tests.

    We use special strategies for `TypeVar` and `Callable` by default, but
    they can be overriden by the user if needed.
    """
    return _Settings(
        settings_kwargs={},
        use_init=False,
        container_strategy=None,
        other_strategies={
            TypeVar: type_vars_factory,  # type: ignore[dict-item]
            Callable: pure_functions_factory,  # type: ignore[dict-item]
        },
    )


@overload
def check_all_laws(
    container_type: type[Lawful[Example_co]],
    *,
    settings_kwargs: dict[str, Any] | None = None,
    container_strategy: StrategyFactory[Example_co] | None = None,
) -> None: ...


@overload
def check_all_laws(
    container_type: type[Lawful[Example_co]],
    *,
    settings_kwargs: dict[str, Any] | None = None,
    use_init: bool = False,
) -> None: ...


def check_all_laws(
    container_type: type[Lawful[Example_co]],
    *,
    settings_kwargs: dict[str, Any] | None = None,
    use_init: bool = False,
    container_strategy: StrategyFactory[Example_co] | None = None,
) -> None:
    """
    Function to check all defined mathematical laws in a specified container.

    Should be used like so:

    .. code:: python

      from returns.contrib.hypothesis.laws import check_all_laws
      from returns.io import IO

      check_all_laws(IO)

    You can also pass different ``hypothesis`` settings inside:

    .. code:: python

      check_all_laws(IO, settings_kwargs={'max_examples': 100})

    Note:
        Cannot be used inside doctests because of the magic we use inside.

    See also:
        - https://sobolevn.me/2021/02/make-tests-a-part-of-your-app
        - https://mmhaskell.com/blog/2017/3/13/obey-the-type-laws

    """
    settings = _Settings(
        settings_kwargs or {},
        use_init,
        container_strategy,
    )

    for interface, laws in container_type.laws().items():
        for law in laws:
            _create_law_test_case(
                container_type,
                interface,
                law,
                settings=settings,
            )


def pure_functions_factory(thing) -> st.SearchStrategy:
    """Factory to create pure functions."""
    like = (
        (lambda: None)
        if len(thing.__args__) == 1
        else (lambda *args, **kwargs: None)
    )
    return_type = thing.__args__[-1]
    return st.functions(
        like=like,
        returns=st.from_type(
            type(None) if return_type is None else return_type,
        ),
        pure=True,
    )


def type_vars_factory(thing: type[object]) -> StrategyFactory:
    """Strategy factory for ``TypeVar``s.

    We ensure that values inside strategies are self-equal. For example,
       ``nan`` does not work for us.
    """
    return types.resolve_TypeVar(thing).filter(  # type: ignore[no-any-return]
        lambda inner: inner == inner,  # noqa: PLR0124, WPS312
    )


@contextmanager
def clean_plugin_context() -> Iterator[None]:
    """
    We register a lot of types in `_entrypoint.py`, we need to clean them.

    Otherwise, some types might be messed up.
    """
    saved_stategies = {}
    for strategy_key, strategy in types._global_type_lookup.items():  # noqa: SLF001
        if isinstance(  # type: ignore[redundant-expr]
            strategy_key,
            type,
        ) and strategy_key.__module__.startswith('returns.'):
            saved_stategies.update({strategy_key: strategy})

    for key_to_remove in saved_stategies:
        types._global_type_lookup.pop(key_to_remove)  # noqa: SLF001
    _clean_caches()

    try:
        yield
    finally:
        for saved_state in saved_stategies.items():
            st.register_type_strategy(*saved_state)


def _clean_caches() -> None:
    st.from_type.__clear_cache()  # type: ignore[attr-defined]  # noqa: SLF001


def _create_law_test_case(
    container_type: type[Lawful],
    interface: type[Lawful],
    law: Law,
    *,
    settings: _Settings,
) -> None:
    test_function = given(st.data())(
        hypothesis_settings(**settings.settings_kwargs)(
            _run_law(container_type, law, settings=settings),
        ),
    )

    called_from = inspect.stack()[2]
    module = inspect.getmodule(called_from[0])

    template = 'test_{container}_{interface}_{name}'
    test_function.__name__ = template.format(  # noqa: WPS125
        container=container_type.__qualname__.lower(),
        interface=interface.__qualname__.lower(),
        name=law.name,
    )

    setattr(
        module,
        test_function.__name__,
        pytest.mark.filterwarnings(
            # We ignore multiple warnings about unused coroutines and stuff:
            'ignore::pytest.PytestUnraisableExceptionWarning',
        )(
            # We mark all tests with `returns_lawful` marker,
            # so users can easily skip them if needed.
            pytest.mark.returns_lawful(test_function),
        ),
    )


def _run_law(
    container_type: type[Lawful],
    law: Law,
    *,
    settings: _Settings,
) -> Callable[[st.DataObject], None]:
    def factory(source: st.DataObject) -> None:
        with ExitStack() as stack:
            stack.enter_context(clean_plugin_context())
            stack.enter_context(
                strategies_for_types(
                    _types_to_strategies(container_type, settings)
                )
            )
            source.draw(st.builds(law.definition))

    return factory


def _types_to_strategies(
    container_type: type[Lawful],
    settings: _Settings,
) -> dict[type[object], StrategyFactory]:
    """Return a mapping from type to `hypothesis` strategy.

    We override the default settings with the user-provided `settings`.
    """
    merged_settings = _default_settings(container_type) | settings
    return merged_settings.other_strategies | _container_mapping(
        container_type, merged_settings
    )


def _container_mapping(
    container_type: type[Lawful],
    settings: _Settings,
) -> dict[type[object], StrategyFactory]:
    """Map `container_type` and its interfaces to the container strategy."""
    container_strategy = _strategy_for_container(container_type, settings)
    return {
        **dict.fromkeys(container_type.laws(), container_strategy),
        container_type: container_strategy,
    }


def _strategy_for_container(
    container_type: type[Lawful],
    settings: _Settings,
) -> StrategyFactory:
    return (
        strategy_from_container(container_type, use_init=settings.use_init)
        if settings.container_strategy is None
        else settings.container_strategy
    )
