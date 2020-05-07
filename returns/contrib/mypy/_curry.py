from collections import namedtuple
from itertools import groupby, product
from operator import itemgetter
from types import MappingProxyType
from typing import (
    ClassVar,
    FrozenSet,
    Iterator,
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
from mypy.types import AnyType, CallableType, FunctionLike, Overloaded
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, TypeVarId

#: Mapping for better `call || function` argument compatibility.
_KIND_MAPPING = MappingProxyType({
    # We have to replace `ARG_OPT` to `ARG_NAMED`,
    # because `ARG_OPT` is only used in function defs, not calls.
    # And `ARG_NAMED` is the same thing for calls.
    ARG_OPT: ARG_NAMED,
})

#: Mapping of `typevar` to real type.
_Constraints = Mapping[TypeVarId, MypyType]

#: Raw material to build `_ArgTree`.
_RawArgTree = List[List[List['_FuncArg']]]

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

    def with_signature(self, new_args: List[_FuncArg]) -> CallableType:
        """Smartly creates a new callable from a given arguments."""
        return detach_callable(self._case_function.copy_modified(
            arg_names=[arg.name for arg in new_args],
            arg_types=[arg.type for arg in new_args],
            arg_kinds=[arg.kind for arg in new_args],
        ))

    def with_ret_type(self, ret_type: MypyType) -> CallableType:
        """Smartly creates a new callable from a given return type."""
        return self._case_function.copy_modified(ret_type=ret_type)

    def _applied_positional_args(
        self,
        applied_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name.name is None,
            applied_args,
        ))

        new_function_args = []
        for ind, arg in enumerate(_FuncArg.from_callable(self._case_function)):
            if arg.kind in self._positional_kinds and ind < len(callee_args):
                new_function_args.append(arg)
        return new_function_args

    def _applied_named_args(
        self,
        applied_args: List[_FuncArg],
    ) -> List[_FuncArg]:
        callee_args = list(filter(
            lambda name: name.name is not None,
            applied_args,
        ))

        new_function_args = []
        for arg in _FuncArg.from_callable(self._case_function):
            has_named_arg_def = any(
                # Argument can either be used as a named argument
                # or passed to `**kwrgs` if it exists.
                arg.name == rdc.name or arg.kind == ARG_STAR2
                for rdc in callee_args
            )
            if callee_args and has_named_arg_def:
                new_function_args.append(arg)
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
        """Finds a diff between two functions' arguments."""
        intermediate_names = [
            arg.name
            for arg in _FuncArg.from_callable(self._intermediate)
        ]
        new_function_args = []

        for ind, arg in enumerate(_FuncArg.from_callable(self._original)):
            should_be_copied = (
                arg.kind in {ARG_STAR, ARG_STAR2} or
                arg.name not in intermediate_names or
                # We need to treat unnamed args differently, because python3.8
                # has pos_only_args, all their names are `None`.
                # This is also true for `lambda` functions where `.name`
                # might be missing for some reason.
                (
                    not arg.name and not (
                        ind < len(intermediate_names) and
                        # If this is also unnamed arg, then ignoring it.
                        not intermediate_names[ind]
                    )
                )
            )
            if should_be_copied:
                new_function_args.append(arg)
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


class PartialFunctionReducer(object):
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
    - How constraints work

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
        intermediate = _Intermediate(case_function).build_callable_type(
            self._applied_args,
        )
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


class CurryFunctionOverloads(object):
    """
    Implementation of ``@curry`` decorator typings.

    Basically does just two things:

    1. Creates all possible ordered combitations of arguments
    2. Creates ``Overload`` instances for functions' return types

    """

    class _ArgTree(object):  # noqa: WPS431
        def __init__(self, case: Optional[CallableType]) -> None:
            self.case = case
            self.children: List['CurryFunctionOverloads._ArgTree'] = []

    def __init__(self, original: CallableType, ctx: FunctionContext) -> None:
        """
        Saving the things we need.

        Args:
            original: original function that was passed to ``@curry``.
            ctx: function context.

        """
        self._original = original
        self._ctx = ctx
        self._overloads: List[CallableType] = []
        self._args = _FuncArg.from_callable(self._original)

        # We need to get rid of generics here.
        # Because, otherwise `detach_callable` with add
        # unused variables to intermediate callables.
        self._default = cast(
            CallableType, self._ctx.default_return_type,
        ).copy_modified(
            ret_type=AnyType(TypeOfAny.implementation_artifact),
        )

    def build_overloads(self) -> MypyType:
        """
        Builds lots of possible overloads for a given function.

        Inside we try to repsent all functions as sequence of arguments,
        grouped by the similar ones and returning one more overload instance.
        """
        if not self._args:  # There's nothing to do, function has 0 args.
            return self._original

        if any(arg.kind in {ARG_STAR, ARG_STAR2} for arg in self._args):
            # We don't support `*args` and `**kwargs`.
            # Because it is very complex. It might be fixes in the future.
            return self._default.ret_type  # Any

        argtree = self._build_argtree(
            self._ArgTree(None),  # starting from root node
            list(self._slices(self._args)),
        )
        self._build_overloads_from_argtree(argtree)
        return self._proper_type(self._overloads)

    def _build_argtree(
        self,
        node: '_ArgTree',
        source: _RawArgTree,
    ) -> '_ArgTree':
        """
        Builds argument tree.

        Each argument can point to zero, one, or more other nodes.
        Arguments that have zero children are treated as bottom (last) ones.
        Arguments that have just one child are meant to be regular functions.
        Arguments that have more than one child are treated as overloads.

        """
        def factory(
            args: _RawArgTree,
        ) -> Iterator[Tuple[List[_FuncArg], _RawArgTree]]:
            if not args or not args[0]:
                return  # we have reached an end of arguments
            yield from (
                (case, [group[1:] for group in grouped])
                for case, grouped in groupby(args, itemgetter(0))
            )

        for case, rest in factory(source):
            new_node = self._ArgTree(
                _Intermediate(self._default).with_signature(case),
            )
            node.children.append(new_node)
            self._build_argtree(source=rest, node=new_node)
        return node

    def _build_overloads_from_argtree(self, argtree: _ArgTree) -> None:
        """Generates functions from argument tree."""
        for child in argtree.children:
            self._build_overloads_from_argtree(child)
            assert child.case  # mypy is not happy  # noqa: S101

            if not child.children:
                child.case = _Intermediate(child.case).with_ret_type(
                    self._original.ret_type,
                )

            if argtree.case is not None:
                # We need to go backwards and to replace the return types
                # of the previous functions. Like so:
                # 1.  `def x -> A`
                # 2.  `def y -> A`
                # Will take `2` and apply its type to the previous function `1`.
                # Will result in `def x -> y -> A`
                # We also overloadify existing return types.
                ret_type = argtree.case.ret_type
                temp_any = isinstance(
                    ret_type, AnyType,
                ) and ret_type.type_of_any == TypeOfAny.implementation_artifact
                argtree.case = _Intermediate(argtree.case).with_ret_type(
                    child.case if temp_any else Overloaded(
                        [child.case, *cast(FunctionLike, ret_type).items()],
                    ),
                )
            else:  # Root is reached, we need to save the result:
                self._overloads.append(child.case)

    def _slices(self, source: List[_FuncArg]) -> Iterator[List[List[_FuncArg]]]:
        """
        Generate all possible slices of a source list.

        Example::

          _slices("AB") ->
            "AB"
            "A" "B"

          _slices("ABC") ->
            "ABC"
            "AB" "C"
            "A" "BC"
            "A" "B" "C"

        """
        for doslice in product([True, False], repeat=len(source) - 1):
            slices = []
            start = 0
            for index, slicehere in enumerate(doslice, 1):
                if slicehere:
                    slices.append(source[start:index])
                    start = index
            slices.append(source[start:])
            yield slices

    def _proper_type(
        self,
        case_functions: List[CallableType],
    ) -> FunctionLike:
        if len(case_functions) == 1:
            return case_functions[0]
        return Overloaded(case_functions)


class AppliedArgs(object):
    """Builds applied args that were partially applied."""

    def __init__(self, function_ctx: FunctionContext) -> None:
        """
        We need the function default context.

        The first arguments of ``partial`` is skipped:
        it is the applied function itself.
        """
        self._function_ctx = function_ctx
        self._parts = zip(
            self._function_ctx.arg_names[1:],
            self._function_ctx.arg_types[1:],
            self._function_ctx.arg_kinds[1:],
        )

    def get_callable_from_context(self) -> MypyType:
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
        checker = self._function_ctx.api.expr_checker  # type: ignore
        function_def = self._function_ctx.arg_types[0][0]

        checker.msg.disable_errors()
        _return_type, function_def = checker.check_call(
            function_def, [], [], self._function_ctx.context, [],
        )
        checker.msg.enable_errors()

        return function_def

    def build_from_context(self) -> Tuple[bool, List[_FuncArg]]:
        """
        Builds handy arguments structures from the context.

        Some usages might be invalid,
        because we cannot really infer some arguments.

        .. code:: python

            partial(some, *args)
            partial(other, **kwargs)

        Here ``*args`` and ``**kwargs`` can be literally anything!
        In these cases we fallback to the default return type.
        """
        applied_args = []
        for names, types, kinds in self._parts:
            for arg in self._generate_applied_args(zip(names, types, kinds)):
                if arg.kind in {ARG_STAR, ARG_STAR2}:
                    # We cannot really work with `*args`, `**kwargs`.
                    return False, []

                applied_args.append(arg)
        return True, applied_args

    def _generate_applied_args(self, arg_parts) -> Iterator[_FuncArg]:
        yield from (
            _FuncArg(name, typ, kind)
            for name, typ, kind in arg_parts
        )
