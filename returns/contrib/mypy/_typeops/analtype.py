from types import MappingProxyType
from typing import List, Optional

from mypy.nodes import ARG_NAMED, ARG_OPT
from mypy.plugin import FunctionContext
from mypy.types import CallableType, FunctionLike

from returns.contrib.mypy._structures.args import FuncArg

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})


def analyze_function_call(
    function: FunctionLike,
    args: List[FuncArg],
    ctx: FunctionContext,
    *,
    show_errors: bool,
) -> Optional[CallableType]:
    """
    Analyzes function call based on passed argumets.

    Internally uses ``check_call`` from ``mypy``.
    It does a lot of magic.

    We also allow to return ``None`` instead of showing errors.
    This might be helpful for cases when we run intermediate analysis.
    """
    checker = ctx.api.expr_checker  # type: ignore
    messages = checker.msg if show_errors else checker.msg.clean_copy()
    return_type, checked_function = checker.check_call(
        function,
        [arg.expression(ctx.context) for arg in args],
        [_KIND_MAPPING.get(arg.kind, arg.kind) for arg in args],
        ctx.context,
        [arg.name for arg in args],
        arg_messages=messages,
    )
    if not show_errors and messages.is_errors():
        return None
    return checked_function
