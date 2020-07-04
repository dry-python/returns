from typing import Callable, cast

from mypy.nodes import TypeInfo
from mypy.plugin import AnalyzeTypeContext, Plugin
from mypy.types import AnyType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny


def analyze(
    plugin: Plugin,
    fullname: str,
) -> Callable[[AnalyzeTypeContext], MypyType]:
    """
    Adds variardiact generics support to ``Kind`` type.

    Without this plugin we would have to use ``Kind``
    with only one type argument.
    Now it is possible to use it with as many type arguments as you wish.

    Here are two examples with one and two type args:

    .. code:: python

      >>> from returns.hkt import Kind
      >>> from typing import TypeVar
      >>> T = TypeVar('T')
      >>> E = TypeVar('E')

      >>> class MyOneTypeArgClass(Kind['MyOneTypeArgClass', T]): ...
      ...

      >>> class MyTwoTypeArgsClass(Kind['MyTwoTypeArgsClass', T, E]): ...
      ...

    This example will also type-check correctly.

    """
    def factory(ctx: AnalyzeTypeContext) -> MypyType:
        type_info = plugin.lookup_fully_qualified(fullname)
        if not type_info:
            return AnyType(TypeOfAny.from_error)

        type_args = [
            ctx.api.analyze_type(type_arg)
            for type_arg in ctx.type.args
        ]
        return Instance(cast(TypeInfo, type_info.node), type_args)
    return factory
