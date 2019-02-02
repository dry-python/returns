# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generic, NoReturn, TypeVar, Union

from typing_extensions import final

from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.monad import Monad, NewValueType, ValueType
from returns.primitives.types import MonadType

_ErrorType = TypeVar('_ErrorType')


# That's the most ugly part.
# We need to express `Either` with two type parameters and
# Left and Right with just one parameter.
# And that's how we do it. Any other and more cleaner ways are appreciated.
class Either(Generic[ValueType, _ErrorType], metaclass=ABCMeta):
    """
    Represents a calculation that may either fail or succeed.

    An alternative to using exceptions.
    'Either' (or its alias 'Result') is an abstract type and should not
    be instantiated directly. Instead use 'Right' (or its alias 'Success')
    and 'Left' (or its alias 'Failure').
    """

    _inner_value: Union[ValueType, _ErrorType]

    @abstractmethod
    def unwrap(self) -> ValueType:  # pragma: no cover
        """
        Custom magic method to unwrap inner value from monad.

        Should be redefined for ones that actually have values.
        And for ones that raise an exception for no values.
        """
        raise NotImplementedError()


@final
class Left(Either[Any, _ErrorType], Monad[_ErrorType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    To help with readability you may alternatively use the alias 'Failure'.
    """

    def __init__(self, inner_value: _ErrorType) -> None:
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)

    def fmap(self, function) -> 'Left[_ErrorType]':
        """Returns the 'Left' instance that was used to call the method."""
        return self

    def bind(self, function) -> 'Left[_ErrorType]':
        """Returns the 'Left' instance that was used to call the method."""
        return self

    def efmap(
        self,
        function: Callable[[_ErrorType], NewValueType],
    ) -> 'Right[NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Right' instance
        and returns a new 'Right' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Right(function(self._inner_value))

    def ebind(self, function: Callable[[_ErrorType], MonadType]) -> MonadType:
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Left' or 'Right' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value: NewValueType) -> NewValueType:
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return default_value

    def unwrap(self) -> NoReturn:
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self) -> _ErrorType:
        """Unwraps inner error value from failed monad."""
        return self._inner_value


@final
class Right(Either[ValueType, Any], Monad[ValueType]):
    """
    Represents a calculation which has succeeded and contains the result.

    To help with readability you may alternatively use the alias 'Success'.
    """

    def __init__(self, inner_value: ValueType) -> None:
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)

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
        function: Callable[[ValueType], MonadType],
    ) -> MonadType:
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Left' or 'Right' type object.
        """
        return function(self._inner_value)

    def efmap(self, function) -> 'Right[ValueType]':
        """Returns the 'Right' instance that was used to call the method."""
        return self

    def ebind(self, function) -> 'Right[ValueType]':
        """Returns the 'Right' instance that was used to call the method."""
        return self

    def value_or(self, default_value: NewValueType) -> ValueType:
        """Returns the value if we deal with 'Right' or default if 'Left'."""
        return self._inner_value

    def unwrap(self) -> ValueType:
        """Returns the unwrapped value from the inside of this monad."""
        return self._inner_value

    def failure(self) -> NoReturn:
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)


# Useful aliases for end users:

Result = Either
Success = Right
Failure = Left
