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
TYPED_FLOW_FUNCTION: Final = 'returns._internal.pipeline.flow.flow'

#: Used for typed ``pipe`` call.
TYPED_PIPE_FUNCTION: Final = 'returns._internal.pipeline.pipe.pipe'
TYPED_PIPE_METHOD: Final = 'returns._internal.pipeline.pipe._Pipe.__call__'

#: Used for HKT emulation.
TYPED_KINDN: Final = 'returns.primitives.hkt.KindN'
TYPED_KINDN_ACCESS: Final = '{0}.'.format(TYPED_KINDN)
TYPED_KIND_DEKIND: Final = 'returns.primitives.hkt.dekind'
TYPED_KIND_KINDED_CALL: Final = 'returns.primitives.hkt.Kinded.__call__'
TYPED_KIND_KINDED_GET: Final = 'returns.primitives.hkt.Kinded.__get__'
