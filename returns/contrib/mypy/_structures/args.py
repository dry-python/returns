from collections import namedtuple
from typing import List, Optional

from mypy.nodes import ArgKind, Context, TempNode
from mypy.types import CallableType
from mypy.types import Type as MypyType
from typing_extensions import final

#: Basic struct to represent function arguments.
_FuncArgStruct = namedtuple('_FuncArgStruct', ('name', 'type', 'kind'))


@final
class FuncArg(_FuncArgStruct):
    """Representation of function arg with all required fields and methods."""

    name: Optional[str]
    type: MypyType  # noqa: WPS125
    kind: ArgKind

    def expression(self, context: Context) -> TempNode:
        """Hack to pass unexisting `Expression` to typechecker."""
        return TempNode(self.type, context=context)

    @classmethod
    def from_callable(cls, function_def: CallableType) -> List['FuncArg']:
        """Public constructor to create FuncArg lists from callables."""
        parts = zip(
            function_def.arg_names,
            function_def.arg_types,
            function_def.arg_kinds,
        )
        return [cls(*part) for part in parts]
