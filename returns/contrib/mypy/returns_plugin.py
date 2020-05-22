"""
Custom mypy plugin to solve the temporary problem with python typing.

Important: we don't do anything ugly here.
We only solve problems of the current typing implementation.

``mypy`` API docs are here:
https://mypy.readthedocs.io/en/latest/extending_mypy.html

We use ``pytest-mypy-plugins`` to test that it works correctly, see:
https://github.com/mkurnikov/pytest-mypy-plugins
"""

from typing import Callable, Mapping, Optional, Type

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Type as MypyType
from typing_extensions import Final, final

from returns.contrib.mypy._features import (
    curry,
    decorators,
    flow,
    partial,
    pointfree,
)

#: Set of full names of our decorators.
_TYPED_DECORATORS: Final = frozenset((
    'returns.result.safe',
    'returns.io.impure',
    'returns.io.impure_safe',
    'returns.maybe.maybe',
    'returns.future.future',
    'returns.future.asyncify',
    'returns.future.future_safe',
    'returns.functions.not_',
))

#: Typed pointfree functions.
_TYPED_POINTFREE_FUNCTIONS: Final = frozenset((
    'returns._generated.pointfree.map._map',
    'returns._generated.pointfree.bind_result._bind_result',
    'returns._generated.pointfree.bind_io._bind_io',
    'returns._generated.pointfree.bind_ioresult._bind_ioresult',
    'returns._generated.pointfree.bind_future._bind_future',
))

#: Used for typed ``partial`` function.
_TYPED_PARTIAL_FUNCTION: Final = 'returns.curry.partial'

#: Used for typed ``curry`` decorator.
_TYPED_CURRY_FUNCTION: Final = 'returns.curry.curry'

#: Used for typed ``flow`` call.
_TYPED_FLOW_FUNCTION: Final = 'returns._generated.pipeline.flow._flow'

#: Type for a function hook.
_FunctionCallback = Callable[[FunctionContext], MypyType]


@final
class _ReturnsPlugin(Plugin):
    _function_hook_plugins: Mapping[str, _FunctionCallback] = {
        _TYPED_PARTIAL_FUNCTION: partial.analyze,
        _TYPED_CURRY_FUNCTION: curry.analyze,
        _TYPED_FLOW_FUNCTION: flow.analyze,
        **dict.fromkeys(_TYPED_POINTFREE_FUNCTIONS, pointfree.analyze),
        **dict.fromkeys(_TYPED_DECORATORS, decorators.analyze),
    }

    def get_function_hook(self, fullname: str) -> Optional[_FunctionCallback]:
        """
        One of the specified ``mypy`` callbacks.

        Runs on each function call in the source code.
        We are only interested in a particular subset of all functions.
        So, we return a function handler for them.

        Otherwise, we return ``None``.
        """
        return self._function_hook_plugins.get(fullname)


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _ReturnsPlugin
