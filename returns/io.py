# -*- coding: utf-8 -*-

from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Generic, TypeVar, overload

from typing_extensions import final

from returns.primitives.container import BaseContainer

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(Generic[_ValueType], BaseContainer):
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
        BaseContainer.__init__(self, inner_value)  # noqa: WPS609

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

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[['IO[_ValueType]'], 'IO[_NewValueType]']:
        """
        Lifts function to be wrapped in ``IO`` for better composition.

        In other words, it modifies the function
        signature from: ``a -> b`` to: ``IO[a] -> IO[b]``

        This is how it should be used:

        .. code:: python

          >>> from returns.io import IO
          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not exactly IO action!
          ...
          >>> IO.lift(example)(IO(2)) == IO(1.0)
          True

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft

        """
        return lambda container: cls.map(container, function)


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
        async def decorator(*args, **kwargs):  # noqa: WPS430
            return IO(await function(*args, **kwargs))
    else:
        def decorator(*args, **kwargs):  # noqa: WPS430
            return IO(function(*args, **kwargs))
    return wraps(function)(decorator)
