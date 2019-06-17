# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union, overload

from typing_extensions import final

from returns.primitives.container import (
    Container,
    FixableContainer,
    GenericContainerOneSlot,
    ValueUnwrapContainer,
)
from returns.primitives.exceptions import UnwrapFailedError

# Aliases:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')


class Maybe(
    GenericContainerOneSlot[_ValueType],
    FixableContainer,
    ValueUnwrapContainer,
    metaclass=ABCMeta,
):
    """
    Represents a result of a series of commutation that can return ``None``.

    An alternative to using exceptions or constant ``is None`` checks.
    ``Maybe`` is an abstract type and should not be instantiated directly.
    Instead use ``Some`` and ``Nothing``.
    """

    @classmethod
    def new(cls, inner_value: Optional[_ValueType]) -> 'Maybe[_ValueType]':
        """Creates new instance of Maybe container based on a value."""
        if inner_value is None:
            return _Nothing(inner_value)
        return _Some(inner_value)

    @abstractmethod  # noqa: A003
    def map(
        self,
        function: Callable[[_ValueType], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':  # pragma: no cover
        """Abstract method to compose container with pure function."""
        raise NotImplementedError()

    @abstractmethod
    def bind(
        self,
        function: Callable[[_ValueType], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':  # pragma: no cover
        """Abstract method to compose container with other container."""
        raise NotImplementedError()

    @abstractmethod
    def fix(
        self,
        function: Callable[[], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':  # pragma: no cover
        """Abstract method to compose container with pure function."""
        raise NotImplementedError()

    @abstractmethod
    def rescue(
        self,
        function: Callable[[], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':  # pragma: no cover
        """Abstract method to compose container with other container."""
        raise NotImplementedError()

    @abstractmethod
    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:  # pragma: no cover
        """Get value or default value."""
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> _ValueType:  # pragma: no cover
        """Get value or raise exception."""
        raise NotImplementedError()

    @abstractmethod
    def failure(self) -> None:  # pragma: no cover
        """Get failed value or raise exception."""
        raise NotImplementedError()


@final  # noqa: Z214
class _Nothing(Maybe[Any]):
    """Represents an empty state."""

    _inner_value: None

    def __init__(self, inner_value: None = None) -> None:  # noqa: Z459
        """
        Wraps the given value in the Container.

        'value' can only be ``None``.
        """
        Container.__init__(self, inner_value)  # type: ignore # noqa: Z462

    def __str__(self):
        """Custom str definition without state inside."""
        return '<Nothing>'

    def map(self, function):  # noqa: A003
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def bind(self, function):
        """Returns the 'Nothing' instance that was used to call the method."""
        return self

    def fix(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should not accept any arguments
        and return a non-container result.
        """
        return Maybe.new(function())

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should not accept any arguments
        and return Maybe a 'Nothing' or 'Some' type object.
        """
        return function()

    def value_or(self, default_value):
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self):
        """Unwraps inner error value from failed container."""
        return self._inner_value


@final
class _Some(Maybe[_ValueType]):
    """
    Represents a calculation which has succeeded and contains the value.

    Quite similar to ``Success`` type.
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Required for typing."""
        Container.__init__(self, inner_value)  # type: ignore # noqa: Z462

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Maybe' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return Maybe.new(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return 'Nothing' or 'Some' type object.
        """
        return function(self._inner_value)

    def fix(self, function):
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def rescue(self, function):
        """Returns the 'Some' instance that was used to call the method."""
        return self

    def value_or(self, default_value):
        """Returns the value if we deal with 'Some' or default if 'Nothing'."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this container."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)


def Some(inner_value: Optional[_ValueType]) -> Maybe[_ValueType]:  # noqa: N802
    """Public unit function of protected `_Some` type."""
    return Maybe.new(inner_value)


#: Public unit value of protected `_Nothing` type.
Nothing: Maybe[Any] = _Nothing()


@overload  # noqa: Z320
def maybe(  # type: ignore
    function: Callable[
        ...,
        Coroutine[_ValueType, _ErrorType, Optional[_NewValueType]],
    ],
) -> Callable[
    ...,
    Coroutine[_ValueType, _ErrorType, Maybe[_NewValueType]],
]:
    """Case for async functions."""


@overload
def maybe(
    function: Callable[..., Optional[_NewValueType]],
) -> Callable[..., Maybe[_NewValueType]]:
    """Case for regular functions."""


def maybe(function):
    """
    Decorator to covert ``None`` returning function to ``Maybe`` container.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):
            regular_result = await function(*args, **kwargs)
            if regular_result is None:
                return Nothing
            return Some(regular_result)
    else:
        def decorator(*args, **kwargs):
            regular_result = function(*args, **kwargs)
            if regular_result is None:
                return Nothing
            return Some(regular_result)
    return wraps(function)(decorator)
