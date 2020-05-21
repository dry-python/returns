from types import MappingProxyType
from typing import List, Optional, overload

from mypy.nodes import ARG_NAMED, ARG_OPT
from mypy.plugin import FunctionContext
from mypy.types import CallableType, FunctionLike
from typing_extensions import Literal

from returns.contrib.mypy._structures.args import FuncArg

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})


@overload
def analyze_call(
    function: FunctionLike,
    args: List[FuncArg],
    ctx: FunctionContext,
    *,
    show_errors: Literal[True],
) -> CallableType:
    """Case when errors are reported and we cannot get ``None``."""


@overload
def analyze_call(
    function: FunctionLike,
    args: List[FuncArg],
    ctx: FunctionContext,
    *,
    show_errors: bool,
) -> Optional[CallableType]:
    """Errors are not reported, we can get ``None`` when errors happen."""


def analyze_call(function, args, ctx, *, show_errors):
    """
    Analyzes function call based on passed argumets.

    Internally uses ``check_call`` from ``mypy``.
    It does a lot of magic.

    We also allow to return ``None`` instead of showing errors.
    This might be helpful for cases when we run intermediate analysis.
    """
    checker = ctx.api.expr_checker
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
