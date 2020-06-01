"""
Typing ``pipe`` functions requires several phases.

It is pretty obvious from its usage:

1. When we pass a sequence of functions we have to reduce
   the final callable type, it is require to match the ``callable`` protocol.
   And at this point we also kinda try
   to check that all pipeline functions do match,
   but this is impossible to do 100% correctly at this point,
   because generic functions don't have a type argument
   to infer the final result

2. When we call the function, we need to check for two things.
   First, we check that passed argument fits our instance requirement.
   Second, we check that pipeline functions match.
   Now we have all arguments to do the real inference.

3. We also need to fix generic in method signature.
   It might be broken, because we add new generic arguments and return type.
   So, it is safe to reattach generic back to the function.

Here's when it works:

.. code:: python

  >>> from returns.pipeline import pipe

  >>> def first(arg: int) -> bool:
  ...     return arg > 0
  >>> def second(arg: bool) -> str:
  ...     return 'bigger' if arg else 'not bigger'

  >>> pipeline = pipe(first, second)  # `analyzed` is called
  >>> assert pipeline(1) == 'bigger'  # `signature and `infer` are called
  >>> assert pipeline(0) == 'not bigger'  # `signature and `infer` again

"""

from typing import Callable, Tuple

from mypy.checker import detach_callable
from mypy.nodes import ARG_POS
from mypy.plugin import FunctionContext, MethodContext, MethodSigContext
from mypy.types import AnyType, CallableType, FunctionLike, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, TypeType, UnionType

from returns.contrib.mypy._typeops.analtype import safe_translate_to_function
from returns.contrib.mypy._typeops.inference import PipelineInference


def _get_first_arg_type(case: CallableType) -> MypyType:
    """Function might not have args at all."""
    if case.arg_types:
        return case.arg_types[0]
    return AnyType(TypeOfAny.implementation_artifact)


def _unify_type(
    function: FunctionLike,
    fetch_type: Callable[[CallableType], MypyType],
) -> MypyType:
    return UnionType.make_union([
        fetch_type(case)
        for case in function.items()
    ])


def _get_pipeline_def(
    ctx: FunctionContext,
) -> Tuple[MypyType, MypyType]:
    first_step = ctx.arg_types[0][0]
    last_step = ctx.arg_types[0][-1]

    if isinstance(first_step, (Instance, TypeType)):
        first_step = safe_translate_to_function(ctx.arg_types[0][0], ctx)
    if isinstance(last_step, (Instance, TypeType)):
        last_step = safe_translate_to_function(ctx.arg_types[0][-1], ctx)
    return first_step, last_step


def analyze(ctx: FunctionContext) -> MypyType:
    """This hook helps when we create the pipeline from sequence of funcs."""
    if not isinstance(ctx.default_return_type, Instance):
        return ctx.default_return_type

    if not ctx.arg_types[0]:  # We do require to pass `*functions` arg.
        ctx.api.fail('Too few arguments for "_pipe"', ctx.context)
        return ctx.default_return_type

    first_step, last_step = _get_pipeline_def(ctx)
    if not isinstance(first_step, FunctionLike):
        return ctx.default_return_type
    if not isinstance(last_step, FunctionLike):
        return ctx.default_return_type

    return ctx.default_return_type.copy_modified(
        args=[
            # First type argument represents first function arguments type:
            _unify_type(first_step, _get_first_arg_type),
            # Second argument represents pipeline final return type:
            _unify_type(last_step, lambda case: case.ret_type),
            # Other types are just functions inside the pipeline:
            *ctx.arg_types[0],
        ],
    )


def infer(ctx: MethodContext) -> MypyType:
    """This hook helps when we finally call the created pipeline."""
    if not isinstance(ctx.type, Instance):
        return ctx.default_return_type

    pipeline_functions = ctx.type.args[2:]
    return PipelineInference(
        ctx.arg_types[0][0],
    ).from_callable_sequence(
        pipeline_functions,
        list((ARG_POS,) * len(pipeline_functions)),
        ctx,
    )


def signature(ctx: MethodSigContext) -> CallableType:
    """Helps to fix generics in method signature."""
    return detach_callable(ctx.default_signature)
