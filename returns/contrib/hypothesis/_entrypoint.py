"""
Used to register all our types as hypothesis strategies.

See: https://hypothesis.readthedocs.io/en/latest/strategies.html

But, beware that we only register concrete types here,
interfaces won't be registered!

TODO: enable this code

.. code:: python

    from typing import Sequence, Type

    from hypothesis import strategies as st

    from returns.context import (
        RequiresContext,
        RequiresContextFutureResult,
        RequiresContextIOResult,
        RequiresContextResult,
    )
    from returns.contrib.hypothesis.containers import strategy_from_container
    from returns.future import Future, FutureResult
    from returns.io import IO, IOResult
    from returns.maybe import Maybe
    from returns.primitives.laws import Lawful
    from returns.result import Result

    _types_to_register: Sequence[Type[Lawful]] = (
        Result,
        Maybe,
        IO,
        IOResult,
        Future,
        FutureResult,
        RequiresContext,
        RequiresContextResult,
        RequiresContextIOResult,
        RequiresContextFutureResult,
    )

    for type_ in _types_to_register:
        st.register_type_strategy(type_, strategy_from_container(type_))

"""
