from mypy.plugin import FunctionContext
from mypy.types import CallableType
from mypy.types import Type as MypyType


def analyze(ctx: FunctionContext) -> MypyType:
    """
    Changes a type of a decorator.

    This problem appears when we try to change the return type of the function.
    However, currently it is impossible due to this bug:
    https://github.com/python/mypy/issues/3157

    It uses the passed function to copy its type.
    We only copy arguments and return type is defined by type annotations.
    """
    if not isinstance(ctx.arg_types[0][0], CallableType):
        return ctx.default_return_type
    if not isinstance(ctx.default_return_type, CallableType):
        return ctx.default_return_type
    return _change_decorator_function_type(
        ctx.default_return_type,
        ctx.arg_types[0][0],
    )


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
