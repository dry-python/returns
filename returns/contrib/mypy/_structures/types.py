from typing import TypeAlias

from mypy.plugin import FunctionContext, MethodContext

CallableContext: TypeAlias = FunctionContext | MethodContext
"""We treat them equally when working with functions or methods."""
