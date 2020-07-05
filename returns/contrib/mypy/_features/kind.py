from typing import Callable, cast

from mypy.nodes import SymbolTableNode, TypeInfo
from mypy.plugin import AnalyzeTypeContext, FunctionContext, Plugin
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
        if not type_info or not ctx.type.args:
            return AnyType(TypeOfAny.from_error)
        return _refine_kind(type_info, ctx)
    return factory


def infer(ctx: FunctionContext) -> MypyType:
    """
    Infers real type behind ``Kind`` form.

    Basically, it turns ``Kind[IO, int]`` into ``IO[int]``.
    The only limitation is that it works with
    only ``Instance`` type in the first type argument position.

    So, ``dekind(Kind[T, int])`` will fail.
    """
    kind = ctx.arg_types[0][0]
    correct_args = (
        isinstance(kind, Instance) and
        isinstance(kind.args[0], Instance)
    )

    if not correct_args:
        ctx.api.fail(
            'dekind should be used with Instance as the first type argument',
            ctx.context,
        )
        return AnyType(TypeOfAny.from_error)

    assert isinstance(kind, Instance)  # mypy requires these lines
    assert isinstance(kind.args[0], Instance)
    return kind.args[0].copy_modified(
        args=kind.args[1:],
    )


def _refine_kind(
    type_info: SymbolTableNode,
    ctx: AnalyzeTypeContext,
) -> Instance:
    type_args = [
        ctx.api.analyze_type(type_arg)
        for type_arg in ctx.type.args
    ]
    return Instance(cast(TypeInfo, type_info.node), type_args)
