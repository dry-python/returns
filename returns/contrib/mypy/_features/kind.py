from enum import Enum, unique
from typing import List, Optional, Sequence

from mypy.checkmember import analyze_member_access
from mypy.plugin import (
    AttributeContext,
    FunctionContext,
    MethodContext,
    MethodSigContext,
)
from mypy.typeops import bind_self, erase_to_bound
from mypy.types import AnyType, CallableType, Instance
from mypy.types import Type as MypyType
from mypy.types import TypeOfAny, TypeVarType, get_proper_type

from returns.contrib.mypy._consts import TYPED_KINDN
from returns.contrib.mypy._typeops.fallback import asserts_fallback_to_any

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
    assert isinstance(ctx.type.args[0], CallableType)
    return ctx.type.args[0]


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
    return _process_kinded_type(ctx.default_return_type)


# @asserts_fallback_to_any
def kinded_get_descriptor(ctx: MethodContext) -> MypyType:
    """
    Used to analyze ``@kinded`` method calls.

    We do this due to ``__get__`` descriptor magic.
    """
    assert isinstance(ctx.type, Instance)
    assert isinstance(ctx.type.args[0], CallableType)

    function = bind_self(ctx.type.args[0])
    assert isinstance(function, CallableType)
    assert isinstance(get_proper_type(function.ret_type), Instance)

    new_ret_type = function.ret_type.copy_modified(
        args=[ctx.arg_types[0][0], *function.ret_type.args[1:]],
    )
    replaced_method = function.copy_modified(ret_type=new_ret_type)
    return ctx.type.copy_modified(args=[replaced_method])


@unique  # noqa: WPS600
class _KindErrors(str, Enum):  # noqa: WPS600
    """Represents a set of possible errors we can throw during typechecking."""

    dekind_not_instance = (
        'dekind must be used with Instance as the first type argument'
    )


def _crop_kind_args(
    kind: Instance,
    limit: Optional[Sequence[MypyType]] = None,
) -> List[MypyType]:
    """Returns the correct amount of type arguments for a kind."""
    if limit is None:
        limit = kind.args[0].args  # type: ignore
    return kind.args[1:len(limit) + 1]


def _process_kinded_type(instance: MypyType) -> MypyType:
    """Recursively process all type arguments in a kind."""
    kind = get_proper_type(instance)
    if not isinstance(kind, Instance) or not kind.args:
        return instance

    if kind.type.fullname != TYPED_KINDN:  # this is some other instance
        return instance

    real_type = get_proper_type(kind.args[0])
    if isinstance(real_type, TypeVarType):
        return erase_to_bound(real_type)
    elif isinstance(real_type, Instance):
        return real_type.copy_modified(args=[
            # Let's check if there are any nested `KindN[]` instance,
            # if so, it would be dekinded into a regular type following
            # the same rules:
            _process_kinded_type(type_arg)
            for type_arg in kind.args[1:len(real_type.args) + 1]
        ])
    # This should never happen, probably can be an exception:
    return AnyType(TypeOfAny.implementation_artifact)
