from collections import Counter, defaultdict, namedtuple
from copy import copy
from types import MappingProxyType
from typing import ClassVar, DefaultDict, FrozenSet, List, Optional, Tuple, Dict

from typing_extensions import final

from mypy.checker import detach_callable
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
from mypy.types import Type as MypyType
from mypy.types import TypeType, UninhabitedType, FunctionLike, CallableType, Overloaded, FormalArgument

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


def _func_args(function_def: CallableType) -> List[_FuncArg]:
    parts = zip(
        function_def.arg_names,
        function_def.arg_types,
        function_def.arg_kinds,
    )
    return [_FuncArg(*part) for part in parts]


@final
class _FunctionModifier(object):
    def __init__(self, function_def: FunctionLike) -> None:
        self._function_def = function_def

    def modify_args(self, new_args: List[List[_FuncArg]]) -> FunctionLike:
        print('new_args', new_args, self._function_def.items())
        print(list(zip(self._function_def.items(), new_args)))
        return self._from_items([
            detach_callable(function_def.copy_modified(
                arg_names=[arg.name for arg in args],
                arg_types=[arg.type for arg in args],
                arg_kinds=[arg.kind for arg in args],
            ))
            for function_def, args in zip(self._function_def.items(), new_args)
        ])

    def modify_ret_type(self, original_defs: FunctionLike) -> FunctionLike:
        return self._from_items([  # TODO: support variables
            function_def.copy_modified(ret_type=original_def.ret_type)
            for function_def, original_def in zip(
                self._function_def.items(),
                original_defs.items(),
            )
        ])

    def _from_items(self, functions: List[CallableType]) -> FunctionLike:
        print('_from_items', functions)  # TODO: _make_proper_function_like
        if len(functions) == 1:
            return functions[0]
        return Overloaded(functions)


@final
class _FunctionDiffer(object):
    def __init__(
        self,
        original: FunctionLike,
        intermediate: CallableType,
        reduced_args: List[_FuncArg],
        ctx: FunctionContext,
    ) -> None:
        self._original = original
        self._intermediate = intermediate
        self._reduced_args = reduced_args
        self._ctx = ctx

    def _get_matching_intermediate_arg(
        self, index: int, arg: _FuncArg,
    ) -> Optional[FormalArgument]:
        if arg.name:
            return self._intermediate.argument_by_name(arg.name)
        return self._intermediate.argument_by_position(index)

    def _is_matching_arg_type(
        self,
        matching: FormalArgument,
        arg: _FuncArg,
    ) -> bool:
        self._ctx.api.msg.disable_errors()  # TODO: create context manager
        same_type = self._ctx.api.check_subtype(
            arg.type,
            matching.typ,
            self._ctx.context,
        )
        self._ctx.api.msg.enable_errors()
        return same_type

    def _make_case_function(
        self,
        function_def: CallableType,
        intermediate: Dict[Optional[str], int],
    ) -> Optional[CallableType]:
        seen_args: DefaultDict[Optional[str], int] = defaultdict(int)
        new_function_args = []

        for index, arg in enumerate(_func_args(function_def)):
            matching_arg = self._get_matching_intermediate_arg(index, arg)
            if matching_arg:
                # TODO: this does not work with `List[T]` and `List[int]`
                is_matching_type = self._is_matching_arg_type(matching_arg, arg)
                print('matching?', matching_arg, arg, is_matching_type)
                if not is_matching_type:
                    return None

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
        return _FunctionModifier(function_def).modify_args([new_function_args])

    def _make_proper_function_like(
        self,
        case_functions: List[CallableType],
    ) -> FunctionLike:  # TODO: this should be a common helper
        if len(case_functions) == 1:
            return case_functions[0]  # This is just a `def`
        return Overloaded(case_functions)  # This is an `@overload [def, ...]`

    def make_diff(self) -> FunctionLike:
        intermediate = Counter(
            arg.name for arg in _func_args(self._intermediate)
        )

        case_functions: List[CallableType] = []

        # TODO: finish this implementation
        for function_def in self._original.items():
            case_function = self._make_case_function(function_def, intermediate)
            if case_function:
                print('case_function', case_function)
                case_functions.append(case_function)
        print('case_functions', case_functions)
        return self._make_proper_function_like(case_functions)


@final
class _ArgumentReducer(object):
    """Helps to tell which callee arguments was already provided in caller."""

    #: Positional arguments can be of this kind.
    _positional_kinds: ClassVar[FrozenSet[int]] = frozenset((
        ARG_POS,
        ARG_OPT,
        ARG_STAR,
    ))

    def __init__(
        self,
        function_def: FunctionLike,
        reduced_args: List[_FuncArg],
        ctx: FunctionContext,
    ) -> None:
        self._function_def = function_def
        self._reduced_args = reduced_args
        self._ctx = ctx
        self._modifier = _FunctionModifier(self._function_def)

    def reduce_existing_args(self) -> FunctionLike:
        """
        By calling this method we construct a new callable from its usage.

        This allows use to create an intermediate callable with just used args.
        """
        new_args = []
        for func_def in self._function_def.items():
            new_pos_args = self._reduce_positional_args(func_def)
            new_named_args = self._reduce_named_args(func_def)
            new_args.append(new_pos_args + new_named_args)
        return self._modifier.modify_args(new_args)

    def _reduce_positional_args(
        self,
        func_def: CallableType,
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is None,
            self._reduced_args,
        ))

        new_function_args = []
        for index, frg in enumerate(_func_args(func_def)):
            if frg.kind in self._positional_kinds and index < len(callee_args):
                new_function_args.append(frg)
        return new_function_args

    def _reduce_named_args(
        self,
        func_def: CallableType,
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is not None,
            self._reduced_args,
        ))

        new_function_args = []
        for frg in _func_args(func_def):
            has_named_arg_def = any(
                # Argument can either be used as a named argument
                # or passed to `**kwrgs` if it exists.
                frg.name == rdc.name or frg.kind == ARG_STAR2
                for rdc in callee_args
            )
            if callee_args and has_named_arg_def:
                new_function_args.append(frg)
        return new_function_args


def analyze_call(
    function_def: FunctionLike,
    args: List[_FuncArg],
    ctx: FunctionContext,
) -> FunctionLike:
    checker = ctx.api.expr_checker  # type: ignore
    return_type, checked_function = checker.check_call(
        function_def,
        [arg.expression(ctx.context) for arg in args],
        [_KIND_MAPPING.get(arg.kind, arg.kind) for arg in args],
        ctx.context,
        [arg.name for arg in args],
    )

    print()
    print('------')
    print(function_def, args)
    print(checker.type_context[-1], checked_function)
    print('------')
    print()

    # for func in function_def.items():
    #     if isinstance(return_type, UninhabitedType):

    # if any(return_type != func.ret_type for func in function_def.items()):
    #     if isinstance(return_type, UninhabitedType):
    #         # This can happen when generic arguments are not given yet.
    #         # By default `mypy` will resolve this ret_type into `NoReturn`
    #         # which is not what we want. So, we keep the old return type.
    #         checked_function = _FunctionModifier(  # TODO: refactor
    #             checked_function,
    #         ).modify_ret_type(function_def)
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
        default_return_type: CallableType,
        original_function: FunctionLike,
        reduced_args: List[_FuncArg],
        ctx: FunctionContext,
    ) -> None:
        """
        Saving the things we need.

        Args:
            default_return_type: default callable type got by ``mypy``.
            original_function: passed function to be curried.
            reduced_args: arguments that are already provided.
            ctx: plugin hook context provided by ``mypy``.

        """
        self._ctx = ctx
        self._reduced_args = reduced_args
        self._default_return_type = default_return_type

        self._original_function = original_function
        self._intermediate_callable = copy(self._original_function)

    def new_partial(self) -> FunctionLike:
        """
        Main method that removes provided arguments from the original function.

        Inside we modify the default return type callable
        and insert right arguments inside it.

        By default it has just ``Any`` arguments type
        for both ``args`` and ``kwargs``.
        """
        self._reduce_intemediate_callable()
        self._reduce_used_in_intermediate()
        return self._default_return_type

    def _reduce_intemediate_callable(self) -> None:
        intermediate = _ArgumentReducer(
            self._intermediate_callable,
            self._reduced_args,
            self._ctx,
        ).reduce_existing_args()
        self._intermediate_callable = analyze_call(
            intermediate,
            self._reduced_args,
            self._ctx,
        )
        print('self._intermediate_callable', self._intermediate_callable)

    def _reduce_used_in_intermediate(self) -> None:
        self._default_return_type = _FunctionDiffer(
            self._original_function,
            self._intermediate_callable,
            self._reduced_args,
            self._ctx,
        ).make_diff()
        print('result', self._default_return_type)
        # TODO: reenable generic support
        # if self._default_return_type.is_generic():
            # If the resulting function is generic,
            # we need an extra round of type-checking and type-inference.
            # We use the combination of passed and declared arguments.
            # This models the substitution of existing arguments by passed ones
            # and leaves untouched arguments for us to proper typecheck them.
            # self._reduce_return_type(new_function_args)
