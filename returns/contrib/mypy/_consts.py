from typing_extensions import Final

# Constant fullnames for typechecking
# ===================================

#: Set of full names of our decorators.
TYPED_DECORATORS: Final = frozenset((
    'returns.result.safe',
    'returns.io.impure',
    'returns.io.impure_safe',
    'returns.maybe.maybe',
    'returns.future.future',
    'returns.future.asyncify',
    'returns.future.future_safe',
    'returns.functions.not_',
))

#: Used for typed ``partial`` function.
TYPED_PARTIAL_FUNCTION: Final = 'returns.curry.partial'

#: Used for typed ``curry`` decorator.
TYPED_CURRY_FUNCTION: Final = 'returns.curry.curry'

#: Used for typed ``flow`` call.
TYPED_FLOW_FUNCTION: Final = 'returns._generated.pipeline.flow._flow'

#: Used for typed ``pipe`` call.
TYPED_PIPE_FUNCTION: Final = 'returns._generated.pipeline.pipe._pipe'
TYPED_PIPE_METHOD: Final = 'returns._generated.pipeline.pipe._Pipe.__call__'

#: Used for HKT emulation.
TYPED_KIND_DEKIND: Final = 'returns.primitives.hkt.dekind'
TYPED_KIND_DEBOUND: Final = 'returns.primitives.hkt.debound'
TYPED_KIND_KINDED: Final = 'returns.primitives.hkt.Kinded.__call__'
