"""
Custom mypy plugin to solve the temporary problem with untyped decorators.

This problem appears when we try to change the return type of the function.
However, currently it is impossible due to this bug:
https://github.com/python/mypy/issues/3157

We also add better support for partial functions.

This plugin is a temporary solution to the problem.
It should be later replaced with the official way of doing things.
One day functions will have better API and we plan
to submit this plugin into ``mypy`` core plugins, so it would not be required.

``mypy`` API docs are here:
https://mypy.readthedocs.io/en/latest/extending_mypy.html

We use ``pytest-mypy-plugins`` to test that it works correctly, see:
https://github.com/mkurnikov/pytest-mypy-plugins
"""

from typing import Callable, Optional, Type

from mypy.plugin import FunctionContext, Plugin
from mypy.types import Type as MypyType
from typing_extensions import final

from returns.contrib.mypy._features import curry, decorators, partial

#: Set of full names of our decorators.
_TYPED_DECORATORS = frozenset((
    'returns.result.safe',
    'returns.io.impure',
    'returns.io.impure_safe',
    'returns.maybe.maybe',
    'returns.future.future',
    'returns.future.asyncify',
    'returns.future.future_safe',
    'returns.functions.not_',
))

#: Used for typed ``partial`` function.
_TYPED_PARTIAL_FUNCTION = 'returns.curry.partial'

#: Used for typed ``curry`` decorator.
_TYPED_CURRY_FUNCTION = 'returns.curry.curry'


@final
class _TypedDecoratorPlugin(Plugin):
    def get_function_hook(
        self, fullname: str,
    ) -> Optional[Callable[[FunctionContext], MypyType]]:
        """
        One of the specified ``mypy`` callbacks.

        Runs on each function call in the source code.
        We are only interested in a particular subset of all functions.
        So, we return a function handler for them.

        Otherwise, we return ``None``.
        """
        if fullname == _TYPED_PARTIAL_FUNCTION:
            return partial.analyze_partial
        elif fullname == _TYPED_CURRY_FUNCTION:
            return curry.analyze_curry
        elif fullname in _TYPED_DECORATORS:
            return decorators.analyze_decorator
        return None


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _TypedDecoratorPlugin
