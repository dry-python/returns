import inspect
import uuid
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Type, Iterator

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.strategies._internal import types

from returns.interfaces.specific.result import ResultLikeN
from returns.interfaces.applicative import ApplicativeN
from returns.primitives.laws import Law, Law1, Law2, Law3, Lawful


@contextmanager
def _temp_container_strategies(container_type: Type[Lawful]) -> Iterator[None]:
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
        types._global_type_lookup.pop(interface)


@contextmanager
def pure_functions() -> Iterator[None]:
    def factory(thing) -> st.SearchStrategy:
        like = (lambda: None) if len(
            thing.__args__,
        ) == 1 else (lambda *a, **k: None)

        return st.functions(
            like=like,
            returns=st.from_type(thing.__args__[-1]),
            pure=True,
        )

    previous = types._global_type_lookup[Callable]  # type: ignore
    st.register_type_strategy(Callable, factory)  # type: ignore

    yield

    types._global_type_lookup.pop(Callable)  # type: ignore
    st.register_type_strategy(Callable, previous)  # type: ignore


def _run_law(
    container_type: Type[Lawful],
    law: Law,
) -> Callable[[st.DataObject], None]:
    def factory(source: st.DataObject) -> None:
        with pure_functions():
            with _temp_container_strategies(container_type):
                source.draw(st.builds(law.definition))
    return factory


def _create_law_test_case(
    container_type: Type[Lawful],
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

    test_function.__name__ = 'test_{container}_{name}_{uuid}'.format(
        container=container_type.__qualname__.lower(),
        name=law.name,
        uuid=str(uuid.uuid4()),
    )

    setattr(module, test_function.__name__, test_function)


def check_all_laws(
    container_type: Type[Lawful],
    *,
    settings_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    for law in container_type.laws():
        _create_law_test_case(
            container_type,
            law,
            settings_kwargs=settings_kwargs,
        )
