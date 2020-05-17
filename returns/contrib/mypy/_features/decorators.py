from mypy.plugin import FunctionContext
from mypy.types import CallableType
from mypy.types import Type as MypyType


def analyze(ctx: FunctionContext) -> MypyType:
    """Tells us what to do when one of the typed decorators is called."""
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
