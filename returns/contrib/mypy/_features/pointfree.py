from mypy.checkmember import analyze_member_access
from mypy.plugin import FunctionContext
from mypy.types import Type as MypyType


def analyze(ctx: FunctionContext) -> MypyType:
    """
    Analyzes several pointfree functions.

    Removes intermediate Protocol instances.
    """
    callee = ctx.default_return_type
    checker = ctx.api.expr_checker  # type: ignore
    return analyze_member_access(
        '__call__',
        callee,
        ctx.context,
        is_lvalue=False,
        is_super=False,
        is_operator=True,
        msg=checker.msg,
        original_type=callee,
        chk=checker.chk,
        in_literal_context=checker.is_literal_context(),
    )
