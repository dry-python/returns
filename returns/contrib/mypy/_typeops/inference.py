from typing import List, Mapping, Optional, cast

from mypy.argmap import map_actuals_to_formals
from mypy.constraints import infer_constraints_for_callable
from mypy.expandtype import expand_type
from mypy.plugin import FunctionContext
from mypy.types import CallableType
from mypy.types import Type as MypyType
from mypy.types import TypeVarId
from typing_extensions import final

from returns.contrib.mypy._structures.args import FuncArg

#: Mapping of `typevar` to real type.
_Constraints = Mapping[TypeVarId, MypyType]


@final
class CallableInference(object):
    """
    Used to infer function arguments and return type.

    There are multiple ways to do it.
    For example, one can infer argument types from its usage.
    """

    def __init__(
        self,
        case_function: CallableType,
        ctx: FunctionContext,
        *,
        fallback: Optional[CallableType] = None,
    ) -> None:
        """
        Create the callable inference.

        Sometimes we need two functions.
        When construction one function from another
        there might be some lost information during the process.
        That's why we optionally need ``fallback``.
        If it is not provided, we treat ``case_function`` as a full one.

        Args:
            case_function: function with solved constaints.
            fallback: Function with unsolved constraints.
            ctx: Function context with checker and expr_checker objects.

        """
        self._case_function = case_function
        self._fallback = fallback if fallback else self._case_function
        self._ctx = ctx

    def from_usage(
        self,
        applied_args: List[FuncArg],
    ) -> CallableType:
        """Infers function constrains from its usage: passed arguments."""
        constraints = self._infer_constraints(applied_args)
        infered = expand_type(self._case_function, constraints)
        return cast(CallableType, infered)

    def _infer_constraints(
        self,
        applied_args: List[FuncArg],
    ) -> _Constraints:
        """Creates mapping of ``typevar`` to real type that we already know."""
        checker = self._ctx.api.expr_checker  # type: ignore
        kinds = [arg.kind for arg in applied_args]
        exprs = [
            arg.expression(self._ctx.context)
            for arg in applied_args
        ]

        formal_to_actual = map_actuals_to_formals(
            kinds,
            [arg.name for arg in applied_args],
            self._fallback.arg_kinds,
            self._fallback.arg_names,
            lambda index: checker.accept(exprs[index]),
        )
        constraints = infer_constraints_for_callable(
            self._fallback,
            [arg.type for arg in applied_args],
            kinds,
            formal_to_actual,
        )
        return {
            constraint.type_var: constraint.target
            for constraint in constraints
        }
