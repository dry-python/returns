from types import MappingProxyType
from typing import List, Optional, overload

from mypy.checkmember import analyze_member_access
from mypy.nodes import ARG_NAMED, ARG_OPT
from mypy.types import CallableType, FunctionLike
from mypy.types import Type as MypyType
from typing_extensions import Final, Literal

from returns.contrib.mypy._structures.args import FuncArg
from returns.contrib.mypy._structures.types import CallableContext

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING: Final = MappingProxyType({
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
    Analyzes function call based on passed arguments.

    Internally uses ``check_call`` from ``mypy``.
    It does a lot of magic.

    We also allow to return ``None`` instead of showing errors.
    This might be helpful for cases when we run intermediate analysis.
    """
    checker = ctx.api.expr_checker
    with checker.msg.filter_errors(save_filtered_errors=True) as local_errors:
        return_type, checked_function = checker.check_call(
            function,
            [arg.expression(ctx.context) for arg in args],
            [_KIND_MAPPING.get(arg.kind, arg.kind) for arg in args],
            ctx.context,
            [arg.name for arg in args],
        )

    if not show_errors and local_errors.has_new_errors():  # noqa: WPS441
        return None

    checker.msg.add_errors(local_errors.filtered_errors())  # noqa: WPS441

    return checked_function


def safe_translate_to_function(
    function_def: MypyType,
    ctx: CallableContext,
) -> MypyType:
    """
    Transforms many other types to something close to callable type.

    There's why we need it:

    - We can use this on real functions
    - We can use this on ``@overload`` functions
    - We can use this on instances with ``__call__``
    - We can use this on ``Type`` types

    It can probably work with other types as well.

    This function allows us to unify this process.
    We also need to disable errors, because we explicitly pass empty args.

    This function also resolves all type arguments.
    """
    checker = ctx.api.expr_checker  # type: ignore
    with checker.msg.filter_errors():
        _return_type, function_def = checker.check_call(
            function_def, [], [], ctx.context, [],
        )
    return function_def


def translate_to_function(
    function_def: MypyType,
    ctx: CallableContext,
) -> MypyType:
    """
    Tryies to translate a type into callable by accessing ``__call__`` attr.

    This might fail with ``mypy`` errors and that's how it must work.
    This also preserves all type arguments as-is.
    """
    checker = ctx.api.expr_checker  # type: ignore
    return analyze_member_access(
        '__call__',
        function_def,
        ctx.context,
        is_lvalue=False,
        is_super=False,
        is_operator=True,
        msg=checker.msg,
        original_type=function_def,
        chk=checker.chk,
        in_literal_context=checker.is_literal_context(),
    )
