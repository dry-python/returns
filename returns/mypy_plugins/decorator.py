# -*- coding: utf-8 -*-

from typing import Callable, Optional, Type

from mypy.types import CallableType
from mypy.plugin import Plugin, FunctionContext

TYPED_DECORATORS = {
    'returns.result.safe',
    'returns.io.impure',
}


def _change_decorator_function_type(
    decorated: CallableType,
    decorator: CallableType,
) -> CallableType:
    decorator.arg_types = decorated.arg_types
    decorator.arg_kinds = decorated.arg_kinds
    decorator.arg_names = decorated.arg_names
    return decorator


def _analyze_decorator(function_ctx: FunctionContext) -> Type:
    return _change_decorator_function_type(
        function_ctx.arg_types[0][0],
        function_ctx.default_return_type,
    )


class TypedDecoratorPlugin(Plugin):
    def get_function_hook(
        self, fullname: str,
    ) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname in TYPED_DECORATORS:
            return _analyze_decorator
        return None


def plugin(version: str):
    return TypedDecoratorPlugin
