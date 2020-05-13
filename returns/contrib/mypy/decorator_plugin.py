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
from mypy.types import CallableType, Instance, Overloaded, TypeType

from returns.contrib.mypy._curry import (
    AppliedArgs,
    CurryFunctionOverloads,
    PartialFunctionReducer,
)

#: Set of full names of our decorators.
_TYPED_DECORATORS = frozenset((
    'returns.result.safe',
    'returns.io.impure',
    'returns.io.impure_safe',
    'returns.maybe.maybe',
    'returns.future.future',
    'returns.future.future_safe',
    'returns.functions.not_',
))

#: Used for typed ``partial`` function.
_TYPED_PARTIAL_FUNCTION = 'returns.curry.partial'

#: Used for typed ``curry`` decorator.
_TYPED_CURRY_FUNCTION = 'returns.curry.curry'


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


def _analyze_partial(function_ctx: FunctionContext):
    """
    This hook is used to make typed curring a thing in `returns` project.

    Internally we just reduce the original function's argument count.
    And drop some of them from function's signature.
    """
    if not isinstance(function_ctx.default_return_type, CallableType):
        return function_ctx.default_return_type

    function_def = function_ctx.arg_types[0][0]
    supported_types = (
        CallableType,
        Instance,
        TypeType,
        Overloaded,
    )

    func_args = AppliedArgs(function_ctx)
    if len(list(filter(len, function_ctx.arg_types))) == 1:
        return function_def  # this means, that `partial(func)` is called
    elif not isinstance(function_def, supported_types):
        return function_ctx.default_return_type
    elif isinstance(function_def, (Instance, TypeType)):
        # We force `Instance` and similar types to coercse to callable:
        function_def = func_args.get_callable_from_context()

    is_valid, applied_args = func_args.build_from_context()
    if not isinstance(function_def, (CallableType, Overloaded)) or not is_valid:
        return function_ctx.default_return_type

    return PartialFunctionReducer(
        function_ctx.default_return_type,
        function_def,
        applied_args,
        function_ctx,
    ).new_partial()


def _analyze_curry(function_ctx: FunctionContext):
    if not isinstance(function_ctx.arg_types[0][0], CallableType):
        return function_ctx.default_return_type
    if not isinstance(function_ctx.default_return_type, CallableType):
        return function_ctx.default_return_type

    x = CurryFunctionOverloads(
        function_ctx.arg_types[0][0],
        function_ctx,
    ).build_overloads()
    print(x)
    return x


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
        if fullname == _TYPED_PARTIAL_FUNCTION:
            return _analyze_partial
        elif fullname == _TYPED_CURRY_FUNCTION:
            return _analyze_curry
        elif fullname in _TYPED_DECORATORS:
            return _analyze_decorator
        return None


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _TypedDecoratorPlugin
