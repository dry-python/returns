"""
Fix for ``*E`` aliases unit methods: ``ResultE``, ``IOResultE``, etc.

Problem: ``IOResultE`` is an alias for ``IOResult[_ValueType_co, Exception]``.
When calling a unit method on the alias, like ``IOResultE.from_value(1)``,
``mypy`` returns ``IOResult[int, Any]`` instead of ``IOResult[int, Exception]``,
because unit constructors use ``Any`` for the type they cannot infer.

This module rewrites the return type of unit constructors
called on ``*E`` aliases: positions where the alias fixes ``Exception``
and the constructor returned ``Any`` are corrected to ``Exception``.

Important: we don't do anything ugly here.
We only solve problems of the current typing implementation.

Related issue: https://github.com/dry-python/returns/issues/407
"""

from mypy.plugin import MethodContext
from mypy.types import (
    AnyType,
    CallableType,
    Instance,
    get_proper_type,
)
from mypy.types import Type as MypyType

_EXCEPTION_FULLNAME = 'builtins.Exception'
"""Fullname of the type ``*E`` aliases fix their error type to."""


def analyze(ctx: MethodContext) -> MypyType:
    """
    Rewrites return type of a unit constructor called on an ``*E`` alias.

    For example, ``IOResultE.from_value(1)`` is rewritten from
    ``IOResult[int, Any]`` to ``IOResult[int, Exception]``.
    """
    self_type = ctx.type
    if not isinstance(self_type, CallableType):
        return ctx.default_return_type

    bound_type = get_proper_type(self_type.ret_type)
    if not isinstance(bound_type, Instance):
        return ctx.default_return_type

    default_ret = get_proper_type(ctx.default_return_type)
    assert isinstance(default_ret, Instance)
    if default_ret.type != bound_type.type:
        # Different containers, nothing to fix.
        return ctx.default_return_type

    new_args = list(default_ret.args)
    changed = False
    for index, (bound_arg, ret_arg) in enumerate(
        zip(bound_type.args, new_args)
    ):
        proper_bound_arg = get_proper_type(bound_arg)
        proper_ret_arg = get_proper_type(ret_arg)
        if (
            isinstance(proper_bound_arg, Instance)
            and proper_bound_arg.type.fullname == _EXCEPTION_FULLNAME
            and isinstance(proper_ret_arg, AnyType)
        ):
            # The alias fixes this position to `Exception`,
            # but the constructor could not infer it and used `Any`.
            new_args[index] = proper_bound_arg
            changed = True

    if not changed:
        return ctx.default_return_type
    return Instance(default_ret.type, new_args, default_ret.line)
