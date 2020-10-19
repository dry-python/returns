from enum import Enum, unique
from typing import Optional, Sequence, Tuple

from mypy.checkmember import analyze_member_access
from mypy.plugin import (
    AttributeContext,
    FunctionContext,
    MethodContext,
    MethodSigContext,
)
from mypy.typeops import bind_self
from mypy.types import AnyType, CallableType, FunctionLike, Instance, Overloaded
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, TypeType, TypeVarType, get_proper_type

from returns.contrib.mypy._typeops.fallback import asserts_fallback_to_any
from returns.contrib.mypy._typeops.visitor import translate_kind_instance

# TODO: probably we can validate `KindN[]` creation during `get_analtype`


@asserts_fallback_to_any
def attribute_access(ctx: AttributeContext) -> MypyType:
    """
    Ensures that attribute access to ``KindN`` is correct.

    In other words:

    .. code:: python

        from typing import TypeVar
        from returns.primitives.hkt import KindN
        from returns.interfaces.mappable import MappableN

        _MappableType = TypeVar('_MappableType', bound=MappableN)

        kind: KindN[_MappableType, int, int, int]
        reveal_type(kind.map)  # will work correctly!

    """
    assert isinstance(ctx.type, Instance)
    instance = ctx.type.args[0]

    if isinstance(instance, TypeVarType):
        bound = get_proper_type(instance.upper_bound)
        assert isinstance(bound, Instance)
        accessed = bound.copy_modified(
            args=_crop_kind_args(ctx.type, bound.args),
        )
    elif isinstance(instance, Instance):
        accessed = instance.copy_modified(args=_crop_kind_args(ctx.type))
    else:
        return ctx.default_attr_type

    exprchecker = ctx.api.expr_checker  # type: ignore
    return analyze_member_access(
        ctx.context.name,  # type: ignore
        accessed,
        ctx.context,
        is_lvalue=False,
        is_super=False,
        is_operator=False,
        msg=ctx.api.msg,
        original_type=instance,
        chk=ctx.api,  # type: ignore
        in_literal_context=exprchecker.is_literal_context(),
    )


def dekind(ctx: FunctionContext) -> MypyType:
    """
    Infers real type behind ``Kind`` form.

    Basically, it turns ``Kind[IO, int]`` into ``IO[int]``.
    The only limitation is that it works with
    only ``Instance`` type in the first type argument position.

    So, ``dekind(KindN[T, int])`` will fail.
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
    return kind.args[0].copy_modified(args=_crop_kind_args(kind))


@asserts_fallback_to_any
def kinded_signature(ctx: MethodSigContext) -> CallableType:
    """
    Returns the internal function wrapped as ``Kinded[def]``.

    Works for ``Kinded`` class when ``__call__`` magic method is used.
    See :class:`returns.primitives.hkt.Kinded` for more information.
    """
    assert isinstance(ctx.type, Instance)
    assert isinstance(ctx.type.args[0], FunctionLike)

    wrapped_method = ctx.type.args[0]
    if isinstance(wrapped_method, Overloaded):
        return ctx.default_signature

    assert isinstance(wrapped_method, CallableType)
    return wrapped_method


# TODO: we should raise an error if bound type does not have any `KindN`
# instances, because that's not how `@kinded` and `Kinded[]` should be used.
def kinded_call(ctx: MethodContext) -> MypyType:
    """
    Reveals the correct return type of ``Kinded.__call__`` method.

    Turns ``-> KindN[I, t1, t2, t3]`` into ``-> I[t1, t2, t3]``.

    Also strips unused type arguments for ``KindN``, so:
    - ``KindN[IO, int, <nothing>, <nothing>]`` will be ``IO[int]``
    - ``KindN[Result, int, str, <nothing>]`` will be ``Result[int, str]``

    It also processes nested ``KindN`` with recursive strategy.

    See :class:`returns.primitives.hkt.Kinded` for more information.
    """
    return translate_kind_instance(ctx.default_return_type)


@asserts_fallback_to_any
def kinded_get_descriptor(ctx: MethodContext) -> MypyType:
    """
    Used to analyze ``@kinded`` method calls.

    We do this due to ``__get__`` descriptor magic.
    """
    assert isinstance(ctx.type, Instance)
    assert isinstance(ctx.type.args[0], CallableType)

    wrapped_method = ctx.type.args[0]
    self_type = wrapped_method.arg_types[0]
    signature = bind_self(
        wrapped_method,
        is_classmethod=isinstance(self_type, TypeType),
    )
    return ctx.type.copy_modified(args=[signature])


@unique  # noqa: WPS600
class _KindErrors(str, Enum):  # noqa: WPS600
    """Represents a set of possible errors we can throw during typechecking."""

    dekind_not_instance = (
        'dekind must be used with Instance as the first type argument'
    )


def _crop_kind_args(
    kind: Instance,
    limit: Optional[Sequence[MypyType]] = None,
) -> Tuple[MypyType, ...]:
    """Returns the correct amount of type arguments for a kind."""
    if limit is None:
        limit = kind.args[0].args  # type: ignore
    return kind.args[1:len(limit) + 1]
