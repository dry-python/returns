from collections import Counter, defaultdict, namedtuple
from types import MappingProxyType
from typing import (
    ClassVar,
    DefaultDict,
    FrozenSet,
    List,
    Mapping,
    Optional,
    Tuple,
    cast,
)

from mypy.argmap import map_actuals_to_formals
from mypy.checker import detach_callable
from mypy.constraints import infer_constraints_for_callable
from mypy.expandtype import expand_type
from mypy.nodes import (
    ARG_NAMED,
    ARG_OPT,
    ARG_POS,
    ARG_STAR,
    ARG_STAR2,
    Context,
    TempNode,
)
from mypy.plugin import FunctionContext
from mypy.types import CallableType, FunctionLike, Overloaded
from mypy.types import Type as MypyType
from mypy.types import TypeVarId

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})

#: Mapping of `typevar` to real type.
_Constraints = Mapping[TypeVarId, MypyType]

#: Basic struct to represent function arguments.
_FuncArgStruct = namedtuple('_FuncArg', ('name', 'type', 'kind'))


class _FuncArg(_FuncArgStruct):
    name: Optional[str]
    type: MypyType  # noqa: WPS125
    kind: int

    def expression(self, context: Context) -> TempNode:
        """Hack to pass unexisting `Expression` to typechecker."""
        return TempNode(self.type, context=context)

    @classmethod
    def from_callable(cls, function_def: CallableType) -> List['_FuncArg']:
        parts = zip(
            function_def.arg_names,
            function_def.arg_types,
            function_def.arg_kinds,
        )
        return [cls(*part) for part in parts]


class _Intermediate(object):
    """Helps to tell which callee arguments was already provided in caller."""

    #: Positional arguments can be of this kind.
    _positional_kinds: ClassVar[FrozenSet[int]] = frozenset((
        ARG_POS,
        ARG_OPT,
        ARG_STAR,
    ))

    def __init__(self, case_function: CallableType) -> None:
        self._case_function = case_function

    def build_callable_type(self, applied_args: List[_FuncArg]) -> CallableType:
        """
        By calling this method we construct a new callable from its usage.

        This allows use to create an intermediate callable with just used args.
        """
        new_pos_args = self._applied_positional_args(applied_args)
        new_named_args = self._applied_named_args(applied_args)
        return self.with_signature(new_pos_args + new_named_args)

    def with_signature(
        self,
        new_args: List[_FuncArg],
        ret_type: Optional[MypyType] = None,
        *,
        skip_detach: bool = False,
    ) -> CallableType:
        new_callable = self._case_function.copy_modified(
            arg_names=[arg.name for arg in new_args],
            arg_types=[arg.type for arg in new_args],
            arg_kinds=[arg.kind for arg in new_args],
            ret_type=ret_type if ret_type else self._case_function.ret_type,
        )
        if skip_detach:
            return new_callable
        return detach_callable(new_callable)

    def _applied_positional_args(
        self,
        applied_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is None,
            applied_args,
        ))

        new_function_args = []
        for ind, frg in enumerate(_FuncArg.from_callable(self._case_function)):
            if frg.kind in self._positional_kinds and ind < len(callee_args):
                new_function_args.append(frg)
        return new_function_args

    def _applied_named_args(
        self,
        applied_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is not None,
            applied_args,
        ))

        new_function_args = []
        for frg in _FuncArg.from_callable(self._case_function):
            has_named_arg_def = any(
                # Argument can either be used as a named argument
                # or passed to `**kwrgs` if it exists.
                frg.name == rdc.name or frg.kind == ARG_STAR2
                for rdc in callee_args
            )
            if callee_args and has_named_arg_def:
                new_function_args.append(frg)
        return new_function_args


class _Functions(object):
    def __init__(
        self,
        original: CallableType,
        intermediate: CallableType,
    ) -> None:
        self._original = original
        self._intermediate = intermediate

    def diff(self) -> CallableType:
        intermediate = Counter(
            arg.name for arg in _FuncArg.from_callable(self._intermediate)
        )

        seen_args: DefaultDict[Optional[str], int] = defaultdict(int)
        new_function_args = []

        for arg in _FuncArg.from_callable(self._original):
            should_be_copied = (
                arg.kind in {ARG_STAR, ARG_STAR2} or
                arg.name not in intermediate or
                # We need to count seen args, because python3.8
                # has pos_only_args, all their names are `None`.
                (not arg.name and seen_args[arg.name] < intermediate[arg.name])
            )
            if should_be_copied:
                new_function_args.append(arg)
                seen_args[arg.name] += 1

        return _Intermediate(self._original).build_callable_type(
            new_function_args,
        )


def _analyze_function_call(
    function: FunctionLike,
    args: List[_FuncArg],
    ctx: FunctionContext,
    *,
    show_errors: bool,
) -> Optional[CallableType]:
    checker = ctx.api.expr_checker  # type: ignore
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


class CurryFunctionReducer(object):
    """
    Helper object to work with curring.

    Here's a quick overview of things that is going on inside:

    1. Firstly we create intermediate callable that represents a subset
       of argument that are passed with the ``curry`` call
    2. Then, we run typechecking on this intermediate function
       and passed arguments to make sure that everything is correct
    3. Then, we substract intermediate arguments from the passed function
    4. Finally we run type substitution on newly created final function
       to replace generic vars we already know to make sure
       that everything still works and the number of type vars is reduced

    This plugin requires several things:

    - One should now how ``ExpressionChecker`` from ``mypy`` works
    - What ``FunctionLike`` is
    - How kinds work in type checking
    - What ``map_actuals_to_formals`` is
    - How contraints work

    That's not an easy plugin to work with.
    """

    def __init__(
        self,
        default_return_type: FunctionLike,
        original: FunctionLike,
        applied_args: List[_FuncArg],
        ctx: FunctionContext,
    ) -> None:
        """
        Saving the things we need.

        Args:
            default_return_type: default callable type got by ``mypy``.
            original: passed function to be curried.
            applied_args: arguments that are already provided in the defition.
            ctx: plugin hook context provided by ``mypy``.

        """
        self._default_return_type = default_return_type
        self._original = original
        self._applied_args = applied_args
        self._ctx = ctx

        self._case_functions: List[CallableType] = []
        self._fallbacks: List[CallableType] = []

    def new_partial(self) -> MypyType:
        """
        Creates new partial functions.

        Splits passed functions into ``case_function``
        where each overloaded spec is processed inducidually.
        Then we combine everything back together removing unfit parts.
        """
        for case_function in self._original.items():
            fallback, intermediate = self._create_intermediate(case_function)
            self._fallbacks.append(fallback)

            if intermediate:
                partial = self._create_partial_case(
                    case_function,
                    intermediate,
                    self._infer_constraints(fallback),
                )
                self._case_functions.append(partial)
        return self._create_new_partial()

    def _create_intermediate(
        self,
        case_function: CallableType,
    ) -> Tuple[CallableType, Optional[CallableType]]:
        intermediate = _Intermediate(
            case_function,
        ).build_callable_type(self._applied_args)
        return intermediate, _analyze_function_call(
            intermediate,
            self._applied_args,
            self._ctx,
            show_errors=False,
        )

    def _infer_constraints(
        self,
        fallback: CallableType,
    ) -> _Constraints:
        """Creates mapping of ``typevar`` to real type that we already know."""
        checker = self._ctx.api.expr_checker  # type: ignore
        kinds = [arg.kind for arg in self._applied_args]
        exprs = [
            arg.expression(self._ctx.context)
            for arg in self._applied_args
        ]

        formal_to_actual = map_actuals_to_formals(
            kinds,
            [arg.name for arg in self._applied_args],
            fallback.arg_kinds,
            fallback.arg_names,
            lambda index: checker.accept(exprs[index]),
        )
        constraints = infer_constraints_for_callable(
            fallback,
            [arg.type for arg in self._applied_args],
            kinds,
            formal_to_actual,
        )
        return {
            constraint.type_var: constraint.target
            for constraint in constraints
        }

    def _create_partial_case(
        self,
        case_function: CallableType,
        intermediate: CallableType,
        constraints: _Constraints,
    ) -> CallableType:
        partial = cast(CallableType, expand_type(
            _Functions(case_function, intermediate).diff(),
            constraints,
        ))
        if case_function.is_generic():
            # We can deal with really different `case_function` over here.
            # The first one is regular `generic` function
            # that has variables and typevars in its spec.
            # In this case, we process `partial` the same way.
            # It should be generic also.
            #
            # The second possible type of `case_function` is pseudo-generic.
            # These are functions that contain typevars in its spec,
            # but variables are empty.
            # Probably these functions are already used in a generic context.
            # So, we ignore them and do not add variables back.
            #
            # Regular functions are also untouched by this.
            return detach_callable(partial)
        return partial.copy_modified(variables=[])

    def _create_new_partial(self) -> MypyType:
        """
        Creates a new partial function-like from set of callables.

        We also need fallbacks here, because sometimes
        there are no possible ways to create at least a single partial case.
        In this scenario we analyze the set of fallbacks
        and tell user what went wrong.
        """
        if not self._case_functions:
            _analyze_function_call(
                self._proper_type(self._fallbacks),
                self._applied_args,
                self._ctx,
                show_errors=True,
            )
            return self._default_return_type
        return self._proper_type(self._case_functions)

    def _proper_type(
        self,
        case_functions: List[CallableType],
    ) -> FunctionLike:
        if len(case_functions) == 1:
            return case_functions[0]
        return Overloaded(case_functions)


def get_callable_from_type(function_ctx: FunctionContext) -> MypyType:
    """
    Returns callable type from the context.

    There's why we need it:

    - We can use ``curry`` on real functions
    - We can use ``curry`` on ``@overload`` functions
    - We can use ``curry`` on instances with ``__call__``
    - We can use ``curry`` on ``Type`` types

    This function allows us to unify this process.
    We also need to disable errors, because we explicitly pass empty args.
    """
    checker = function_ctx.api.expr_checker  # type: ignore
    function_def = function_ctx.arg_types[0][0]

    checker.msg.disable_errors()
    _return_type, function_def = checker.check_call(
        function_def, [], [], function_ctx.context, [],
    )
    checker.msg.enable_errors()

    return function_def


def make_reduced_args(function_ctx: FunctionContext) -> List[_FuncArg]:
    """Utility to convert passed arguments from function to our format."""
    parts = zip(
        function_ctx.arg_names[1:],
        function_ctx.arg_types[1:],
        function_ctx.arg_kinds[1:],
    )

    reduced_args = []
    for names, types, kinds in parts:
        reduced_args.extend([
            _FuncArg(*part)
            for part in zip(names, types, kinds)
        ])
    return reduced_args
