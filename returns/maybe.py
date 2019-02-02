# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Callable, NoReturn, Union, overload

from typing_extensions import Literal, final

from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.monad import Monad, NewValueType, ValueType
from returns.primitives.types import MonadType


class Maybe(Monad[ValueType], metaclass=ABCMeta):
    """
    Represents a result of a series of commutation that can return ``None``.

    An alternative to using exceptions.
    ``Maybe`` is an abstract type and should not be instantiated directly.
    Instead use ``Some`` and ``Nothing``.
    """

    @overload
    @classmethod
    def new(cls, inner_value: Literal[None]) -> 'Nothing':  # type: ignore
        """Overload to declare correct return type for Nothing."""

    @overload  # noqa: F811
    @classmethod
    def new(cls, inner_value: ValueType) -> 'Some[ValueType]':
        """Overload to declare correct return type for Some."""

    @classmethod  # noqa: F811
    def new(
        cls, inner_value: Union[ValueType, Literal[None]],
    ) -> Union['Nothing', 'Some[ValueType]']:
        """Creates new instance of Some or Nothing monads based on a value."""
        if inner_value is None:
            return Nothing(inner_value)
        return Some(inner_value)


@final
class Nothing(Maybe[Literal[None]]):
    """Represents an empty state."""

    _inner_value: Literal[None]

    def __init__(self, inner_value: Literal[None] = None) -> None:
        """
        Wraps the given value in the Container.

        'value' can only be ``None``.
        """
        object.__setattr__(self, '_inner_value', inner_value)

    def fmap(self, function) -> 'Nothing':
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def bind(self, function) -> 'Nothing':
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def efmap(
        self,
        function: Callable[[Literal[None]], 'NewValueType'],
    ) -> 'Some[NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Some(function(self._inner_value))

    def ebind(
        self,
        function: Callable[[Literal[None]], MonadType],
    ) -> MonadType:
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Nothing' or 'Some' type object.
        """
        return function(self._inner_value)

    def value_or(self, default_value: NewValueType) -> NewValueType:
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return default_value

    def unwrap(self) -> NoReturn:
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self) -> None:
        """Unwraps inner error value from failed monad."""
        return self._inner_value


@final
class Some(Maybe[ValueType]):
    """
    Represents a calculation which has succeeded and contains the result.

    Quite similar to ``Success`` type.
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
    ) -> 'Some[NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should accept a single "normal" (non-monad) argument
        and return a non-monad result.
        """
        return Some(function(self._inner_value))

    def bind(
        self,
        function: Callable[[ValueType], MonadType],
    ) -> MonadType:
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-monad) argument
        and return either a 'Nothing' or 'Some' type object.
        """
        return function(self._inner_value)

    def efmap(self, function) -> 'Some[ValueType]':
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def ebind(self, function) -> 'Some[ValueType]':
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def value_or(self, default_value: NewValueType) -> ValueType:
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return self._inner_value

    def unwrap(self) -> ValueType:
        """Returns the unwrapped value from the inside of this monad."""
        return self._inner_value

    def failure(self) -> NoReturn:
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)
