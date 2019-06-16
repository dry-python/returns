# -*- coding: utf-8 -*-

"""
Custom mypy plugin to solve the temporary problem with untyped decorators.

This problem appears when we try to change the return type of the function.
However, currently it is impossible due to this bug:
https://github.com/python/mypy/issues/3157

This plugin is a temporary solution to the problem.
It should be later replaced with the official way of doing things.

``mypy`` API docs are here:
https://mypy.readthedocs.io/en/latest/extending_mypy.html

We use ``pytest-mypy-plugins`` to test that it works correctly, see:
https://github.com/mkurnikov/pytest-mypy-plugins
"""

from typing import Callable, Optional, Type

from mypy.plugin import FunctionContext, Plugin
from mypy.types import CallableType

#: Set of full names of our decorators.
_TYPED_DECORATORS = {
    'returns.result.safe',
    'returns.io.impure',
    'returns.maybe.maybe',
}


def _change_decorator_function_type(
    decorator: CallableType,
    arg_type: CallableType,
) -> CallableType:
    """Replaces revealed argument types by mypy with types from decorated."""
    return decorator.copy_modified(
        arg_types=arg_type.arg_types,
        arg_kinds=arg_type.arg_kinds,
        arg_names=arg_type.arg_names,
        variables=arg_type.variables,
        is_ellipsis_args=arg_type.is_ellipsis_args,
    )


def _analyze_decorator(function_ctx: FunctionContext):
    """Tells us what to do when one of the typed decorators is called."""
    if not isinstance(function_ctx.arg_types[0][0], CallableType):
        return function_ctx.default_return_type
    if not isinstance(function_ctx.default_return_type, CallableType):
        return function_ctx.default_return_type
    return _change_decorator_function_type(
        function_ctx.default_return_type,
        function_ctx.arg_types[0][0],
    )


class _TypedDecoratorPlugin(Plugin):
    def get_function_hook(  # type: ignore
        self, fullname: str,
    ) -> Optional[Callable[[FunctionContext], Type]]:
        """
        One of the specified ``mypy`` callbacks.

        Runs on each function call in the source code.
        We are only interested in a particular subset of all functions.
        So, we return a function handler for them.

        Otherwise, we return ``None``.
        """
        if fullname in _TYPED_DECORATORS:
            return _analyze_decorator
        return None


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _TypedDecoratorPlugin
