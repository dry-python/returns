# -*- coding: utf-8 -*-

from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, TypeVar, overload

from typing_extensions import final

from returns.primitives.container import Container, GenericContainerOneSlot

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(GenericContainerOneSlot[_ValueType]):
    """
    Explicit marker for impure function results.

    We call it "marker" since once it is marked, it cannot be unmarked.

    ``IO`` is also a container.
    But, it is different in a way
    that it cannot be unwrapped / rescued / fixed.
    There's no way to directly get its internal value.
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Required for typing."""
        Container.__init__(self, inner_value)  # type: ignore # noqa: Z462

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'IO[_NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the IO instance
        and returns a new IO object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return IO(function(self._inner_value))

    def bind(
        self, function: Callable[[_ValueType], 'IO[_NewValueType]'],
    ) -> 'IO[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return IO type object.
        """
        return function(self._inner_value)


@overload
def impure(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _NewValueType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, IO[_NewValueType]],
]:
    """Case for async functions."""


@overload
def impure(
    function: Callable[..., _NewValueType],
) -> Callable[..., IO[_NewValueType]]:
    """Case for regular functions."""


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
