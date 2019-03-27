# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, TypeVar

from returns.primitives.container import GenericContainerTwoSlots
from returns.primitives.exceptions import UnwrapFailedError

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


class Result(
    GenericContainerTwoSlots[_ValueType, _ErrorType],
    metaclass=ABCMeta,
):
    """Base class for Failure and Success."""


class Failure(Result[Any, _ErrorType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    To help with readability you may alternatively use the alias 'Failure'.
    """

    def map(self, function):  # noqa: A003
        """Returns the 'Failure' instance that was used to call the method."""
        return self

    def bind(self, function):
        """Returns the 'Failure' instance that was used to call the method."""
        return self

    def fix(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Success' instance
        and returns a new 'Success' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Success(function(self._inner_value))

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return Result a 'Failure' or 'Success' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value):
        """Returns the value if we deal with 'Success' or default otherwise."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        if isinstance(self._inner_value, Exception):
            raise UnwrapFailedError(self) from self._inner_value

        raise UnwrapFailedError(self)

    def failure(self):
        """Unwraps inner error value from failed monad."""
        return self._inner_value


class Success(Result[_ValueType, Any]):
    """
    Represents a calculation which has succeeded and contains the result.

    To help with readability you may alternatively use the alias 'Success'.
    """

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Success' instance
        and returns a new 'Success' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Success(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return Result a 'Failure' or 'Success' type object.
        """
        return function(self._inner_value)

    def fix(self, function):
        """Returns the 'Success' instance that was used to call the method."""
        return self

    def rescue(self, function):
        """Returns the 'Success' instance that was used to call the method."""
        return self

    def value_or(self, default_value):
        """Returns the value if we deal with 'Success' or default otherwise."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this monad."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)
