import dataclasses
import inspect
from collections.abc import Callable, Iterator, Mapping
from contextlib import ExitStack, contextmanager
from typing import Any, TypeGuard, TypeVar, final, overload

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from hypothesis.strategies._internal import types  # noqa: PLC2701

from returns.contrib.hypothesis.containers import strategy_from_container
from returns.contrib.hypothesis.type_resolver import (
    StrategyFactory,
    strategies_for_types,
)
from returns.primitives.laws import LAWS_ATTRIBUTE, Law, Lawful

Example_co = TypeVar('Example_co', covariant=True)


@final
@dataclasses.dataclass(frozen=True)
class _Settings:
    """Settings that we provide to an end user."""

    settings_kwargs: dict[str, Any]
    use_init: bool
    container_strategy: StrategyFactory | None

    def __post_init__(self) -> None:
        """Check that the settings are mutually compatible."""
        if self.use_init and self.container_strategy is not None:
            raise AssertionError(
                'Expected only one of `use_init` and'
                ' `container_strategy` to be truthy'
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


@contextmanager
def interface_strategies(
    container_type: type[Lawful],
    *,
    settings: _Settings,
) -> Iterator[None]:
    """
    Make all interfaces of a container resolve to the container's strategy.

    For example, let's say we have ``Result`` type.
    It is a subtype of ``ContainerN``, ``MappableN``, ``BindableN``, etc.
    When we check this type, we need ``MappableN`` to resolve to ``Result``.

    Can be used independently from other functions.
    """
    mapping: Mapping[type[object], StrategyFactory] = {
        interface: _strategy_for_container(container_type, settings)
        for interface in lawful_interfaces(container_type)
    }
    with strategies_for_types(mapping):
        yield


@contextmanager
def register_container(
    container_type: type['Lawful'],
    *,
    settings: _Settings,
) -> Iterator[None]:
    """Temporary registers a container if it is not registered yet."""
    with strategies_for_types({
        container_type: _strategy_for_container(container_type, settings)
    }):
        yield


@contextmanager
def pure_functions() -> Iterator[None]:
    """
    Context manager to resolve all ``Callable`` as pure functions.

    It is not a default in ``hypothesis``.
    """

    def factory(thing) -> st.SearchStrategy:
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

    used = types._global_type_lookup[Callable]  # type: ignore[index]  # noqa: SLF001
    st.register_type_strategy(Callable, factory)  # type: ignore[arg-type]

    try:
        yield
    finally:
        types._global_type_lookup.pop(Callable)  # type: ignore[call-overload]  # noqa: SLF001
        st.register_type_strategy(Callable, used)  # type: ignore[arg-type]


@contextmanager
def type_vars() -> Iterator[None]:
    """
    Our custom ``TypeVar`` handling.

    There are several noticeable differences:

    1. We add mutable types to the tests: like ``list`` and ``dict``
    2. We ensure that values inside strategies are self-equal,
       for example, ``nan`` does not work for us

    """

    def factory(thing):
        return types.resolve_TypeVar(thing).filter(
            lambda inner: inner == inner,  # noqa: PLR0124, WPS312
        )

    used = types._global_type_lookup.pop(TypeVar)  # noqa: SLF001
    st.register_type_strategy(TypeVar, factory)

    try:
        yield
    finally:
        types._global_type_lookup.pop(TypeVar)  # noqa: SLF001
        st.register_type_strategy(TypeVar, used)


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


def lawful_interfaces(container_type: type[Lawful]) -> set[type[Lawful]]:
    """Return ancestors of `container_type` that are lawful interfaces."""
    return {
        base_type
        for base_type in container_type.__mro__
        if _is_lawful_interface(base_type)
        and base_type not in {Lawful, container_type}
    }


def _is_lawful_interface(
    interface_type: type[object],
) -> TypeGuard[type[Lawful]]:
    return issubclass(interface_type, Lawful) and _has_non_inherited_attribute(
        interface_type, LAWS_ATTRIBUTE
    )


def _has_non_inherited_attribute(type_: type[object], attribute: str) -> bool:
    return attribute in type_.__dict__


def _clean_caches() -> None:
    st.from_type.__clear_cache()  # type: ignore[attr-defined]  # noqa: SLF001


def _strategy_for_container(
    container_type: type[Lawful],
    settings: _Settings,
) -> StrategyFactory:
    return (
        strategy_from_container(container_type, use_init=settings.use_init)
        if settings.container_strategy is None
        else settings.container_strategy
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
            stack.enter_context(type_vars())
            stack.enter_context(pure_functions())
            stack.enter_context(
                interface_strategies(container_type, settings=settings),
            )
            stack.enter_context(
                register_container(container_type, settings=settings),
            )
            source.draw(st.builds(law.definition))

    return factory


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
