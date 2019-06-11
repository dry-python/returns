# -*- coding: utf-8 -*-

from functools import wraps
from inspect import iscoroutinefunction
from typing import TypeVar

from returns.primitives.container import GenericContainerOneSlot

_ValueType = TypeVar('_ValueType')


class IO(GenericContainerOneSlot[_ValueType]):
    """
    Explicit marker for impure function results.

    We call it "marker" since once it is marked, it cannot be unmarked.

    ``IO`` is also a container.
    But, it is different in a way
    that it cannot be unwrapped / rescued / fixed.
    There's no way to directly get its internal value.
    """

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the IO instance
        and returns a new IO object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return IO(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return IO type object.
        """
        return function(self._inner_value)


def impure(function):
    """
    Decorator to mark function that it returns :py:class:`IO` container.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):
            return IO(await function(*args, **kwargs))
    else:
        def decorator(*args, **kwargs):
            return IO(function(*args, **kwargs))
    return wraps(function)(decorator)
