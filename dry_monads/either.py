# -*- coding: utf-8 -*-

from typing import Callable

from dry_monads.primitives.monad import Monad, NewValueType, ValueType


class Either(Monad[ValueType]):
    """
    Represents a calculation that may either fail or succeed.

    An alternative to using exceptions.
    'Either' (or its alias 'Result') is an abstract type and should not
    be instantiated directly. Instead use 'Right' (or its alias 'Success')
    and 'Left' (or its alias 'Failure')
    """


class Left(Either[ValueType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    To help with readability you may alternatively use the alias 'Failure'.
    """

    def fmap(self, function) -> 'Left[ValueType]':
        """Returns the 'Left' instance that was used to call the method."""
        return Left(self._inner_value)

    def bind(self, function) -> 'Left[ValueType]':
        """Returns the 'Left' instance that was used to call the method."""
        return Left(self._inner_value)

    def value_or(self, default_value: NewValueType) -> NewValueType:
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return default_value


class Right(Either[ValueType]):
    """
    Represents a calculation which has succeeded and contains the result.

    To help with readability you may alternatively use the alias 'Success'.
    """

    def fmap(
        self,
        function: Callable[[ValueType], NewValueType],
    ) -> 'Right[NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Right' instance
        and returns a new 'Right' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Right(function(self._inner_value))

    def bind(
        self,
        function: Callable[[ValueType], Either[NewValueType]],
    ) -> Either[NewValueType]:
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Left' or 'Right' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value: NewValueType) -> ValueType:
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return self._inner_value


# Useful aliases for end users:

Result = Either
Success = Right
Failure = Left
