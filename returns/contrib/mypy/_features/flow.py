from typing import cast

from mypy.nodes import ARG_POS
from mypy.plugin import FunctionContext
from mypy.types import CallableType, FunctionLike
from mypy.types import Type as MypyType

from returns.contrib.mypy._structures.args import FuncArg
from returns.contrib.mypy._typeops.analtype import analyze_call


def analyze(ctx: FunctionContext) -> MypyType:
    """
    Helps to analyze ``flow`` function calls.

    By default, ``mypy`` cannot infer and check this function call:

    .. code:: python

      >>> from returns.pipeline import flow
      >>> assert flow(
      ...     1,
      ...     lambda x: x + 1,
      ...     lambda y: y / 2,
      ... ) == 1.0

    But, this plugin can!
    It knows all the types for all ``lambda`` functions in the pipeline.
    How?

    1. We use the first passed parameter as the first argument
       to the first passed function
    2. We use parameter + function to check the call and reveal
       types of current pipeline step
    3. We iterate through all passed function and use previous
       return type as a new parameter to call current function

    """
    if not ctx.arg_types[0]:
        return ctx.default_return_type
    if not ctx.arg_types[1]:  # We do require to pass `*functions` arg.
        ctx.api.fail('Too few arguments for "_flow"', ctx.context)
        return ctx.default_return_type
    return _infer_pipeline(ctx)


def _infer_pipeline(ctx: FunctionContext) -> MypyType:
    parameter = FuncArg(None, ctx.arg_types[0][0], ARG_POS)
    ret_type = ctx.default_return_type

    for pipeline, kind in zip(ctx.arg_types[1], ctx.arg_kinds[1]):
        ret_type = _proper_type(
            analyze_call(
                cast(FunctionLike, pipeline),
                [parameter],
                ctx,
                show_errors=True,
            ),
        )
        parameter = FuncArg(None, ret_type, kind)
    return ret_type


def _proper_type(typ: MypyType) -> MypyType:
    if isinstance(typ, CallableType):
        return typ.ret_type
    return typ  # It might be `Instance` or `AnyType`
