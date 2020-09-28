from typing import Callable, Optional

from mypy.nodes import ARG_POS, SymbolTableNode
from mypy.plugin import FunctionContext
from mypy.types import CallableType
from mypy.types import Type as MypyType

from returns.contrib.mypy._structures.args import FuncArg
from returns.contrib.mypy._typeops import analtype


def analyze(
    sym: Optional[SymbolTableNode],
) -> Callable[[FunctionContext], MypyType]:
    """
    Changes a type of a decorator.

    This problem appears when we try to change the return type of the function.
    However, currently it is impossible due to this bug:
    https://github.com/python/mypy/issues/3157

    It uses the passed function to copy its type.
    We only copy arguments and return type is defined by type annotations.
    """
    def factory(ctx: FunctionContext) -> MypyType:
        if not (sym and sym.type and isinstance(sym.type, CallableType)):
            return ctx.default_return_type

        arg = ctx.api.expr_checker.accept(ctx.args[0][0])  # type: ignore
        tp = analtype.analyze_call(
            sym.type,
            [FuncArg(None, arg, ARG_POS)],
            ctx,
            show_errors=False,
        )

        if not (isinstance(arg, CallableType) and isinstance(tp, CallableType)):
            return ctx.default_return_type
        if not isinstance(tp.ret_type, CallableType):
            return ctx.default_return_type
        return _change_decorator_function_type(tp.ret_type, arg)
    return factory


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
