from types import MappingProxyType
from typing import List, Optional, overload

from mypy.nodes import ARG_NAMED, ARG_OPT
from mypy.types import CallableType, FunctionLike
from mypy.types import Type as MypyType
from typing_extensions import Literal

from returns.contrib.mypy._structures.args import FuncArg
from returns.contrib.mypy._structures.types import CallableContext

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
    ctx: CallableContext,
    *,
    show_errors: Literal[True],
) -> CallableType:
    """Case when errors are reported and we cannot get ``None``."""


@overload
def analyze_call(
    function: FunctionLike,
    args: List[FuncArg],
    ctx: CallableContext,
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


def safe_translate_to_function(
    function_def: MypyType,
    ctx: CallableContext,
) -> MypyType:
    """
    Tranforms many other types to something close to callable type.

    There's why we need it:

    - We can use this on real functions
    - We can use this on ``@overload`` functions
    - We can use this on instances with ``__call__``
    - We can use this on ``Type`` types

    It can probably work with other types as well.

    This function allows us to unify this process.
    We also need to disable errors, because we explicitly pass empty args.
    """
    checker = ctx.api.expr_checker  # type: ignore
    checker.msg.disable_errors()
    _return_type, function_def = checker.check_call(
        function_def, [], [], ctx.context, [],
    )
    checker.msg.enable_errors()
    return function_def
