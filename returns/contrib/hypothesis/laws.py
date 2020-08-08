from hypothesis import strategies as st
from hypothesis import given, settings
from typing import Callable, Optional, Dict, Any

import pytest
import inspect
from returns.primitives.laws import Law, Lawful, Law1, Law2, Law3

_default_strategy = st.integers()


def _run_law(
    container_type,
    law: Law,
    *,
    strategy: Optional[st.SearchStrategy],
) -> Callable[[st.DataObject], None]:
    strategy_to_use = strategy or _default_strategy

    def factory(source: st.DataObject) -> None:
        arg1 = source.draw(strategy_to_use)
        arg2 = source.draw(strategy_to_use)
        arg3 = source.draw(strategy_to_use)

        if isinstance(law, Law1):
            law.run(
                container_type.from_value(arg1),
            )
        elif isinstance(law, Law2):
            law.run(
                container_type.from_value(arg1),
                container_type.from_value(arg2),
            )
        elif isinstance(law, Law3):
            law.run(
                container_type.from_value(arg1),
                container_type.from_value(arg2),
                container_type.from_value(arg3),
            )
        else:
            assert False, 'Type {0} is not valid as a Law'.format(type(law))
    return factory


def _create_law_test_case(
    container_type: Lawful,
    law: Law,
    *,
    strategy: Optional[st.SearchStrategy],
    settings_kwargs: Optional[Dict[str, Any]],
) -> None:
    if settings_kwargs is None:
        settings_kwargs = {}

    test_function = given(st.data())(
        settings(**settings_kwargs)(
            _run_law(container_type, law, strategy=strategy),
        ),
    )

    called_from = inspect.stack()[2]
    module = inspect.getmodule(called_from[0])

    test_function.__name__ = 'test_{container}_{name}'.format(
        container=container_type.__qualname__.lower(),  # type: ignore
        name=law.name,
    )

    setattr(module, test_function.__name__, test_function)


def check_all_laws(
    container_type: Lawful,
    *,
    strategy: Optional[st.SearchStrategy] = None,
    settings_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    for law in container_type.laws():
        _create_law_test_case(
            container_type,
            law,
            strategy=strategy,
            settings_kwargs=settings_kwargs,
        )
