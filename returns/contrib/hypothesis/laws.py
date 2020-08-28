import inspect
from contextlib import contextmanager
from typing import Any, Callable, Dict, Iterator, List, Optional, Type

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.strategies._internal import types

from returns.interfaces.applicative import ApplicativeN
from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.laws import Law, Lawful


def check_all_laws(
    container_type: Type[Lawful],
    *,
    settings_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Function to check all definied mathematical laws in a specified container.

    Should be used like so:

    .. code:: python

      from returns.contrib.hypothesis.laws import check_all_laws
      from returns.io import IO

      check_all_laws(IO)

    You can also pass different ``hypothesis`` settings inside:

    .. code:: python

      check_all_laws(IO, {'max_examples': 100})

    Note:
        Cannot be used inside doctests because of the magic we use inside.

    See: https://mmhaskell.com/blog/2017/3/13/obey-the-type-laws
    """
    for interface, laws in container_type.laws().items():
        for law in laws:
            _create_law_test_case(
                container_type,
                interface,
                law,
                settings_kwargs=settings_kwargs,
            )


@contextmanager
def container_strategies(container_type: Type[Lawful]) -> Iterator[None]:
    """
    Registers all types inside a container to resolve to a correct strategy.

    For example, let's say we have ``Result`` type.
    It is a subtype of ``ContainerN``, ``MappableN``, ``BindableN``, etc.
    When we check this type, we need ``MappableN`` to resolve to ``Result``.

    Can be used independently from other functions.
    """
    def factory(type_) -> st.SearchStrategy:
        strategies: List[st.SearchStrategy[Any]] = []
        if issubclass(container_type, ApplicativeN):
            strategies.append(st.builds(container_type.from_value))
        if issubclass(container_type, ResultLikeN):
            strategies.append(st.builds(container_type.from_failure))
        return st.one_of(*strategies)

    interfaces = {
        base_type
        for base_type in container_type.__mro__
        if getattr(base_type, '__module__', '').startswith('returns.')
    }
    for interface in interfaces:
        st.register_type_strategy(interface, factory)

    yield

    for interface in interfaces:
        types._global_type_lookup.pop(interface)  # noqa: WPS441


@contextmanager
def pure_functions() -> Iterator[None]:
    """
    Context manager to resolve all ``Callable`` as pure functions.

    It is not a default in ``hypothesis``.
    """
    def factory(thing) -> st.SearchStrategy:
        like = (lambda: None) if len(
            thing.__args__,
        ) == 1 else (lambda *args, **kwargs: None)

        return st.functions(
            like=like,
            returns=st.from_type(thing.__args__[-1]),
            pure=True,
        )

    used = types._global_type_lookup[Callable]  # type: ignore
    st.register_type_strategy(Callable, factory)  # type: ignore

    yield

    types._global_type_lookup.pop(Callable)  # type: ignore
    st.register_type_strategy(Callable, used)  # type: ignore


def _run_law(
    container_type: Type[Lawful],
    law: Law,
) -> Callable[[st.DataObject], None]:
    def factory(source: st.DataObject) -> None:
        with pure_functions():
            with container_strategies(container_type):
                source.draw(st.builds(law.definition))
    return factory


def _create_law_test_case(
    container_type: Type[Lawful],
    interface: Type[Lawful],
    law: Law,
    *,
    settings_kwargs: Optional[Dict[str, Any]],
) -> None:
    if settings_kwargs is None:
        settings_kwargs = {}

    test_function = given(st.data())(
        settings(**settings_kwargs)(
            _run_law(container_type, law),
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
        # We mark all tests with `returns_lawful` marker,
        # so users can easily skip them if needed.
        pytest.mark.returns_lawful(test_function),
    )
