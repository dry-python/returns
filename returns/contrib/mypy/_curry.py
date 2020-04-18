from collections import Counter, defaultdict, namedtuple
from copy import copy
from types import MappingProxyType
from typing import ClassVar, DefaultDict, FrozenSet, List, Optional

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
from mypy.types import CallableType
from mypy.types import Type as MypyType
from mypy.types import TypeType, UninhabitedType

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})

#: Basic struct to represent function arguments.
_FuncArgStruct = namedtuple('_FuncArg', ('name', 'type', 'kind'))


class _FuncArg(_FuncArgStruct):
    name: Optional[str]
    type: MypyType  # noqa: WPS125
    kind: int

    def expression(self, context: Context) -> TempNode:
        """Hack to pass unexisting `Expression` to typechecker."""
        return TempNode(self.type, context=context)


def _func_args(has_args: CallableType) -> List[_FuncArg]:
    parts = zip(
        has_args.arg_names,
        has_args.arg_types,
        has_args.arg_kinds,
    )
    return [_FuncArg(*part) for part in parts]


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


class _ArgumentReducer(object):
    """Helps to tell which callee arguments was already provided in caller."""

    #: Positional arguments can be of this kind.
    _positional_kinds: ClassVar[FrozenSet[int]] = frozenset((
        ARG_POS,
        ARG_OPT,
        ARG_STAR,
    ))

    def __init__(self, function_def: CallableType) -> None:
        self._function_def = function_def

    def apply_new_args(
        self,
        new_args: List[_FuncArg],
    ) -> CallableType:
        """Reassignes the default return type with new arguments."""
        return detach_callable(self._function_def.copy_modified(
            arg_names=[arg.name for arg in new_args],
            arg_types=[arg.type for arg in new_args],
            arg_kinds=[arg.kind for arg in new_args],
        ))

    def reduce_existing_args(
        self, reduced_args: List[_FuncArg],
    ) -> CallableType:
        """
        By calling this method we construct a new callable.

        This allows use to create an intermediate callable
        alongside with the arguments that were used during the curring.
        """
        new_pos_args = self._reduce_positional_args(reduced_args)
        new_named_args = self._reduce_named_args(reduced_args)
        return self.apply_new_args(new_pos_args + new_named_args)

    def _reduce_positional_args(
        self, reduced_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is None,
            reduced_args,
        ))

        new_function_args = []
        for index, frg in enumerate(_func_args(self._function_def)):
            if frg.kind in self._positional_kinds and index < len(callee_args):
                new_function_args.append(frg)
        return new_function_args

    def _reduce_named_args(
        self, reduced_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name[0] is not None,
            reduced_args,
        ))

        new_function_args = []
        for frg in _func_args(self._function_def):
            has_named_arg_def = any(
                # Argument can either be used as a named argument
                # or passed to `**kwrgs` if it exists.
                frg.name == rdc.name or frg.kind == ARG_STAR2
                for rdc in callee_args
            )
            if callee_args and has_named_arg_def:
                new_function_args.append(frg)
        return new_function_args


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
    - What ``CallableType`` is
    - How kinds work in type checking
    - What ``map_actuals_to_formals`` is

    That's not an easy plugin to work with.
    """

    def __init__(
        self,
        default_return_type: CallableType,
        original_function: CallableType,
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
        self._default_return_type = default_return_type
        self._original_function = original_function
        self._intermediate_callable = copy(self._original_function)
        self._reduced_args = reduced_args
        self._ctx = ctx

    def new_partial(self) -> CallableType:
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
        arguments = _ArgumentReducer(self._intermediate_callable)
        self._intermediate_callable = self._analyze_call(
            arguments.reduce_existing_args(self._reduced_args),
            self._reduced_args,
        )

    def _analyze_call(
        self, function_def: CallableType, new_args: List[_FuncArg],
    ) -> CallableType:
        checker = self._ctx.api.expr_checker  # type: ignore
        return_type, checked_function = checker.check_call(
            function_def,
            [new_arg.expression(self._ctx.context) for new_arg in new_args],
            [
                _KIND_MAPPING.get(new_arg.kind, new_arg.kind)
                for new_arg in new_args
            ],
            self._ctx.context,
            [new_arg.name for new_arg in new_args],
        )
        if return_type != function_def.ret_type:
            if isinstance(return_type, UninhabitedType):
                # This can happen when generic arguments are not given yet.
                # By default `mypy` will resolve this ret_type into `NoReturn`
                # which is not what we want. So, we keep the old return type.
                checked_function = checked_function.copy_modified(
                    ret_type=function_def.ret_type,
                )
        return checked_function

    def _reduce_used_in_intermediate(self) -> None:
        intermediate = Counter(
            arg.name for arg in _func_args(self._intermediate_callable)
        )
        seen_args: DefaultDict[Optional[str], int] = defaultdict(int)
        new_function_args = []

        for arg in _func_args(self._original_function):
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

        self._default_return_type = _ArgumentReducer(
            self._default_return_type,
        ).apply_new_args(new_function_args)
        if self._default_return_type.is_generic():
            # If the resulting function is generic,
            # we need an extra round of type-checking and type-inference.
            # We use the combination of passed and declared arguments.
            # This models the substitution of existing arguments by passed ones
            # and leaves untouched arguments for us to proper typecheck them.
            self._reduce_return_type(new_function_args)

    def _reduce_return_type(self, new_args: List[_FuncArg]) -> None:
        compound = self._analyze_call(
            self._original_function,
            self._reduced_args + new_args,
        )
        self._default_return_type = self._default_return_type.copy_modified(
            ret_type=compound.ret_type,
            variables=compound.variables,
        )
        if not isinstance(self._ctx.arg_types[0][0], TypeType):
            # When we pass `Type[T]` to our `curry` function,
            # we don't need to add type variables back. But!
            # When working with regular callables, we absoultely need to.
            self._default_return_type = detach_callable(
                self._default_return_type,
            )
