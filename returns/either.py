# -*- coding: utf-8 -*-

from abc import ABCMeta

from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.monad import Monad


class Either(Monad, metaclass=ABCMeta):
    """Base class for Left and Right."""


class Left(Either):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    To help with readability you may alternatively use the alias 'Failure'.
    """

    def fmap(self, function):
        """Returns the 'Left' instance that was used to call the method."""
        return self

    def bind(self, function):
        """Returns the 'Left' instance that was used to call the method."""
        return self

    def efmap(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Right' instance
        and returns a new 'Right' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Right(function(self._inner_value))

    def ebind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Left' or 'Right' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value):
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self):
        """Unwraps inner error value from failed monad."""
        return self._inner_value


class Right(Either):
    """
    Represents a calculation which has succeeded and contains the result.

    To help with readability you may alternatively use the alias 'Success'.
    """

    def fmap(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Right' instance
        and returns a new 'Right' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Right(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Left' or 'Right' type object.
        """
        return function(self._inner_value)

    def efmap(self, function):
        """Returns the 'Right' instance that was used to call the method."""
        return self

    def ebind(self, function):
        """Returns the 'Right' instance that was used to call the method."""
        return self

    def value_or(self, default_value):
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this monad."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)


# Useful aliases for end users:

Result = Either
Success = Right
Failure = Left
