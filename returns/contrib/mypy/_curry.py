from typing_extensions import final
from mypy.nodes import Context, TempNode, CallExpr, NameExpr
from mypy.types import CallableType, FunctionLike, Type as MypyType, Overloaded, ARG_POS, ARG_STAR, ARG_STAR2, ARG_OPT, ARG_NAMED, TypeType, UninhabitedType, UnionType
from mypy.plugin import FunctionContext
from mypy.checker import detach_callable
from typing import List, Optional, ClassVar, FrozenSet, Tuple
from collections import namedtuple, Counter, defaultdict
from types import MappingProxyType
from contextlib import contextmanager
from mypy.messages import MessageBuilder
from itertools import zip_longest
from mypy.stats import is_generic
from copy import copy

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})

#: Basic struct to represent function arguments.
_FuncArgStruct = namedtuple('_FuncArg', ('name', 'type', 'kind'))


@final
class _FuncArg(_FuncArgStruct):
    name: Optional[str]
    type: MypyType  # noqa: WPS125
    kind: int

    def expression(self, context: Context) -> TempNode:
        """Hack to pass unexisting `Expression` to typechecker."""
        return TempNode(self.type, context=context)


def _func_args(function_def: CallableType) -> List[_FuncArg]:
    parts = zip(
        function_def.arg_names,
        function_def.arg_types,
        function_def.arg_kinds,
    )
    return [_FuncArg(*part) for part in parts]


@final
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
        for index, frg in enumerate(_func_args(self._case_function)):
            if frg.kind in self._positional_kinds and index < len(callee_args):
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
        for frg in _func_args(self._case_function):
            has_named_arg_def = any(
                # Argument can either be used as a named argument
                # or passed to `**kwrgs` if it exists.
                frg.name == rdc.name or frg.kind == ARG_STAR2
                for rdc in callee_args
            )
            if callee_args and has_named_arg_def:
                new_function_args.append(frg)
        return new_function_args


@final
class _Functions(object):
    def __init__(self, original: CallableType, intermediate: CallableType) -> None:
        self._original = original
        self._intermediate = intermediate

    def diff(self) -> CallableType:
        intermediate = Counter(
            arg.name for arg in _func_args(self._intermediate)
        )

        seen_args: DefaultDict[Optional[str], int] = defaultdict(int)
        new_function_args = []

        for arg in _func_args(self._original):
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

    def mix(self) -> CallableType:
        original_args = _func_args(self._original)
        intermediate_args = _func_args(self._intermediate)

        if len(original_args) == len(intermediate_args):
            return self._intermediate
        return self._original
        # new_function_args = []
        # for arg1, arg2 in zip_longest(original_args, intermediate_args):
        #     new_function_args.append(arg2 if arg2 else arg1)

        # return _Intermediate(self._original).with_signature(
        #     new_function_args,
        #     skip_detach=True,
        # )


def _analyze_function_call(
    function: FunctionLike,
    args: List[_FuncArg],
    ctx: CallableType,
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


@final
class CurryFunctionReducer(object):
    """
    Helper object to work with curring.

    Here's a quick overview of things that is going on inside:

    1. Firstly we create intermediate callable that represents a subset
       of argument that are passed with the ``curry`` call.
    2. Then, we run typechecking on this intermediate function
       and passed arguments to make sure that everything is correct
    3. Then, we substract intermediate arguments from the passed function
    4. We run typechecking again on newly created final function
       to copy generic attributes and make sure that everything still works

    This plugin requires several things:

    - One should now how ``ExpressionChecker`` from ``mypy`` works
    - What ``FunctionLike`` is
    - How kinds work in type checking
    - What ``map_actuals_to_formals`` is

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

    def new_partial(self) -> FunctionLike:
        case_functions = []
        fallbacks = []

        for case_function in self._original.items():
            fallback, intermediate = self._create_intermediate(case_function)
            fallbacks.append(fallback)
            if intermediate:
                partial = self._create_partial_case(case_function, intermediate)
                case_functions.append(partial)
        return self._create_new_partial(case_functions, fallbacks)

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

    def _create_partial_case(
        self,
        case_function: CallableType,
        intermediate: CallableType,
    ) -> CallableType:
        partial = _Functions(
            case_function,
            intermediate,
        ).diff()
        return self._solve_generics(case_function, intermediate, partial)

    def _solve_generics(
        self,
        case_function: CallableType,
        intermediate: CallableType,
        partial: CallableType,
    ) -> CallableType:
        if not partial.is_generic():
            return partial

        compound = _analyze_function_call(
            _Functions(case_function, intermediate).mix(),
            self._applied_args + _func_args(partial),
            self._ctx,
            show_errors=True,
        )
        print()
        print('origin', case_function)
        print('intermediate', intermediate)
        print('mix', _Functions(case_function, intermediate).mix())
        print('partial', partial)
        print('compound', compound, self._applied_args + _func_args(partial))
        print()
        partial = partial.copy_modified(
            ret_type=compound.ret_type,
            variables=compound.variables,
        )
        if not isinstance(self._ctx.arg_types[0][0], TypeType):
            # When we pass `Type[T]` to our `curry` function,
            # we don't need to add type variables back. But!
            # When working with regular callables, we absoultely need to.
            partial = detach_callable(partial)
        return partial

    def _create_new_partial(
        self,
        case_functions: List[CallableType],
        fallbacks: List[CallableType],
    ) -> MypyType:
        if not case_functions:
            _analyze_function_call(
                self._proper_type(fallbacks),
                self._applied_args,
                self._ctx,
                show_errors=True,
            )
            return self._default_return_type
        return self._proper_type(case_functions)

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
