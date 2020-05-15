from mypy.plugin import FunctionContext
from mypy.types import CallableType
from mypy.types import Type as MypyType


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


def analyze_decorator(function_ctx: FunctionContext) -> MypyType:
    """Tells us what to do when one of the typed decorators is called."""
    if not isinstance(function_ctx.arg_types[0][0], CallableType):
        return function_ctx.default_return_type
    if not isinstance(function_ctx.default_return_type, CallableType):
        return function_ctx.default_return_type
    return _change_decorator_function_type(
        function_ctx.default_return_type,
        function_ctx.arg_types[0][0],
    )
