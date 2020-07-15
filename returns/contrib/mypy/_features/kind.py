from enum import Enum, unique
from typing import cast

from mypy.plugin import FunctionContext, MethodContext, MethodSigContext
from mypy.typeops import erase_to_bound
from mypy.types import AnyType, CallableType, Instance, TupleType
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, TypeVarType, get_proper_type

# TODO: probably we can validate `KindN[]` creation during `get_analtype`


def dekind(ctx: FunctionContext) -> MypyType:
    """
    Infers real type behind ``Kind`` form.

    Basically, it turns ``Kind[IO, int]`` into ``IO[int]``.
    The only limitation is that it works with
    only ``Instance`` type in the first type argument position.

    So, ``dekind(Kind[T, int])`` will fail.
    """
    kind = get_proper_type(ctx.arg_types[0][0])
    correct_args = (
        isinstance(kind, Instance) and
        isinstance(kind.args[0], Instance)
    )

    if not correct_args:
        ctx.api.fail(_KindErrors.dekind_not_instance, ctx.context)
        return AnyType(TypeOfAny.from_error)

    assert isinstance(kind, Instance)  # mypy requires these lines
    assert isinstance(kind.args[0], Instance)
    return kind.args[0].copy_modified(
        args=kind.args[1:len(kind.args[0].args) + 1],
    )


def debound(ctx: FunctionContext) -> MypyType:
    """
    Analyzes the proper return type of ``debound`` function.

    Uses the ``upper_bound`` of ``TypeVar`` to infer the type of a ``Kind``.

    Here's a quick example:

    .. code:: python

      from typing import TypeVar
      from returns.primitives.hkt import Kind1, debound
      from returns.interfaces import Bindable1

      B = TypeVar('B', bound=Bindable1)

      x: Kind1[B, int]
      instance, rebound = debound(x)
      reveal_type(instance)  # Revealed type: 'Bindable[int]'

    See :func:`returns.primitives.hkt.debound` for more information.

    """
    if not isinstance(ctx.default_return_type, TupleType):
        return AnyType(TypeOfAny.from_error)
    if not ctx.arg_types or not ctx.arg_types[0][0]:
        return AnyType(TypeOfAny.from_error)

    kind = cast(Instance, ctx.arg_types[0][0])
    typevar = kind.args[0]
    if not isinstance(typevar, TypeVarType):
        ctx.api.fail(_KindErrors.debound_not_typevar, ctx.context)
        return AnyType(TypeOfAny.from_error)

    bound = get_proper_type(erase_to_bound(typevar))
    if not isinstance(bound, Instance):
        ctx.api.fail(_KindErrors.debound_not_typevar, ctx.context)
        return AnyType(TypeOfAny.from_error)

    instance = bound.copy_modified(args=kind.args[1:])
    return ctx.default_return_type.copy_modified(
        items=[instance, ctx.default_return_type.items[1]],
    )


def kinded_signature(ctx: MethodSigContext) -> CallableType:
    """
    Returns the internal function wrapped as ``Kinded[def]``.

    Works for ``Kinded`` class when ``__call__`` magic method is used.
    See :class:`returns.primitives.hkt.Kinded` for more information.
    """
    assert isinstance(ctx.type, Instance)
    assert isinstance(ctx.type.args[0], CallableType)
    return ctx.type.args[0]


def kinded_method(ctx: MethodContext) -> MypyType:
    """
    Reveals the correct return type of ``Kinded.__call__`` method.

    Turns ``KindN[I, t1, t2, t3]`` into ``I[t1, t2, t3]``.

    Also strips unused type arguments for ``KindN``, so:
    - ``KindN[IO, int, <nothing>, <nothing>]`` will be ``IO[int]``
    - ``KindN[Result, int, str, <nothing>]`` will be ``Result[int, str]``

    It also processes nested ``KindN`` with recursive strategy.

    See :class:`returns.primitives.hkt.Kinded` for more information.
    """
    return _process_kinded_type(ctx.default_return_type)


@unique  # noqa: WPS600
class _KindErrors(str, Enum):  # noqa: WPS600
    """Represents a set of possible errors we can throw during typechecking."""

    dekind_not_instance = (
        'dekind must be used with Instance as the first type argument'
    )
    debound_not_typevar = (
        'debound must be used with bound TypeVar as the first type argument'
    )


def _process_kinded_type(kind: MypyType) -> MypyType:
    """Recursively process all type arguments in a kind."""
    kind = get_proper_type(kind)
    if not isinstance(kind, Instance) or not kind.args:
        return kind

    real_type = kind.args[0]
    if isinstance(real_type, TypeVarType):
        return erase_to_bound(real_type)
    elif isinstance(real_type, AnyType):
        return real_type

    real_type = get_proper_type(real_type)
    if isinstance(real_type, Instance):
        return real_type.copy_modified(args=[
            # Let's check if there are any nested `KindN[]` instance,
            # if so, it would be dekinded into a regular type following
            # the same rules:
            _process_kinded_type(type_arg)
            for type_arg in kind.args[1:len(real_type.args) + 1]
        ])
    return kind
