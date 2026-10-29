from typing import Final

# Constant fullnames for typechecking
# ===================================

TYPED_PARTIAL_FUNCTION: Final = 'returns.curry.partial'
"""Used for typed ``partial`` function."""

TYPED_CURRY_FUNCTION: Final = 'returns.curry.curry'
"""Used for typed ``curry`` decorator."""

TYPED_FLOW_FUNCTION: Final = 'returns._internal.pipeline.flow.flow'
"""Used for typed ``flow`` call."""

TYPED_PIPE_FUNCTION: Final = 'returns._internal.pipeline.pipe.pipe'
TYPED_PIPE_METHOD: Final = 'returns._internal.pipeline.pipe._Pipe.__call__'
"""Used for typed ``pipe`` call."""

TYPED_KINDN: Final = 'returns.primitives.hkt.KindN'
TYPED_KINDN_ACCESS: Final = f'{TYPED_KINDN}.'
TYPED_KIND_DEKIND: Final = 'returns.primitives.hkt.dekind'
TYPED_KIND_KINDED_CALL: Final = 'returns.primitives.hkt.Kinded.__call__'
TYPED_KIND_KINDED_GET: Final = 'returns.primitives.hkt.Kinded.__get__'
"""Used for HKT emulation."""

DO_NOTATION_METHODS: Final = (
    # Just validation:
    'returns.io.IO.do',
    'returns.maybe.Maybe.do',
    'returns.future.Future.do',
    # Also infer error types:
    'returns.result.Result.do',
    'returns.io.IOResult.do',
    'returns.future.FutureResult.do',
)
"""Used for :ref:`do-notation`."""

E_ALIAS_METHODS: Final = (
    # ``Result`` unit constructors:
    'returns.result.Result.from_value',
    'returns.result.Result.from_failure',
    'returns.result.Result.from_result',
    # ``IOResult`` unit constructors:
    'returns.io.IOResult.from_typecast',
    'returns.io.IOResult.from_failed_io',
    'returns.io.IOResult.from_io',
    'returns.io.IOResult.from_result',
    'returns.io.IOResult.from_ioresult',
    'returns.io.IOResult.from_value',
    'returns.io.IOResult.from_failure',
    # ``FutureResult`` unit constructors:
    'returns.future.FutureResult.from_typecast',
    'returns.future.FutureResult.from_future',
    'returns.future.FutureResult.from_failed_future',
    'returns.future.FutureResult.from_future_result',
    'returns.future.FutureResult.from_io',
    'returns.future.FutureResult.from_failed_io',
    'returns.future.FutureResult.from_ioresult',
    'returns.future.FutureResult.from_result',
    'returns.future.FutureResult.from_value',
    'returns.future.FutureResult.from_failure',
    # ``RequiresContextResult`` unit constructors:
    'returns.context.requires_context_result.RequiresContextResult.from_result',
    'returns.context.requires_context_result.RequiresContextResult.from_typecast',
    'returns.context.requires_context_result.RequiresContextResult.from_value',
    'returns.context.requires_context_result.RequiresContextResult.from_failure',
    # ``RequiresContextIOResult`` unit constructors:
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_result',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_io',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_failed_io',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_ioresult',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_typecast',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_value',
    'returns.context.requires_context_ioresult.RequiresContextIOResult.from_failure',
    # ``RequiresContextFutureResult`` unit constructors:
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_result',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_io',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_failed_io',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_ioresult',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_future',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_failed_future',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_future_result',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_typecast',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_value',
    'returns.context.requires_context_future_result.RequiresContextFutureResult.from_failure',
)
"""Used for ``*E`` aliases unit methods."""

E_ALIAS_ANALYZER: Final = 'returns.contrib.mypy._features.alias_e.analyze'
"""Used for ``*E`` aliases unit methods."""
