# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import TypeVar

from typing_extensions import Literal

from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.monad import GenericMonadOneSlot

_ValueType = TypeVar('_ValueType')


class Maybe(GenericMonadOneSlot[_ValueType], metaclass=ABCMeta):
    """
    Represents a result of a series of commutation that can return ``None``.

    An alternative to using exceptions.
    ``Maybe`` is an abstract type and should not be instantiated directly.
    Instead use ``Some`` and ``Nothing``.
    """

    @classmethod
    def new(cls, inner_value):
        """Creates new instance of Some or Nothing monads based on a value."""
        if inner_value is None:
            return Nothing(inner_value)
        return Some(inner_value)


class Nothing(Maybe[Literal[None]]):
    """Represents an empty state."""

    def __init__(self, inner_value=None):
        """
        Wraps the given value in the Container.

        'value' can only be ``None``.
        """
        object.__setattr__(self, '_inner_value', inner_value)

    def fmap(self, function):
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def bind(self, function):
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def efmap(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Some(function(self._inner_value))

    def ebind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return Result a 'Nothing' or 'Some' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value):
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self):
        """Unwraps inner error value from failed monad."""
        return self._inner_value


class Some(Maybe[_ValueType]):
    """
    Represents a calculation which has succeeded and contains the result.

    Quite similar to ``Success`` type.
    """

    def fmap(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Some(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return Result a 'Nothing' or 'Some' type object.
        """
        return function(self._inner_value)

    def efmap(self, function):
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def ebind(self, function):
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def value_or(self, default_value):
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this monad."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)
