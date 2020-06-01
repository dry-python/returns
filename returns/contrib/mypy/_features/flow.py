from mypy.plugin import FunctionContext
from mypy.types import Type as MypyType

from returns.contrib.mypy._typeops.inference import PipelineInference


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

    return PipelineInference(
        ctx.arg_types[0][0],
    ).from_callable_sequence(
        ctx.arg_types[1],
        ctx.arg_kinds[1],
        ctx,
    )
