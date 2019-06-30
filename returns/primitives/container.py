# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, NoReturn, TypeVar, Union

from typing_extensions import Protocol, runtime

from returns.primitives.exceptions import ImmutableStateError

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')


class BaseContainer(object, metaclass=ABCMeta):
    """Utility class to provide all needed magic methods to the context."""

    __slots__ = ('_inner_value',)
    _inner_value: Any

    def __init__(self, inner_value):
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)  # noqa: Z462

    def __setattr__(self, attr_name: str, attr_value) -> NoReturn:
        """Makes inner state of the containers immutable."""
        raise ImmutableStateError()

    def __delattr__(self, attr_name: str) -> NoReturn:  # noqa: Z434
        """Makes inner state of the containers immutable."""
        raise ImmutableStateError()

    def __str__(self) -> str:
        """Converts to string."""
        return '<{0}: {1}>'.format(
            self.__class__.__qualname__.strip('_'),
            str(self._inner_value),
        )

    def __eq__(self, other) -> bool:
        """Used to compare two 'Container' objects."""
        if type(self) != type(other):
            return False
        return self._inner_value == other._inner_value  # noqa: Z441


@runtime
class Bindable(Protocol[_ValueType]):
    """
    Represents a "context" in which calculations can be executed.

    ``Bindable`` allows you to bind together
    a series of calculations while maintaining
    the context of that specific container.
    """

    def bind(
        self, function: Callable[[_ValueType], 'Bindable[_NewValueType]'],
    ) -> 'Bindable[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new container.
        Works for containers that represent success.
        Is the opposite of :meth:`Rescueable.rescue`.
        """


@runtime
class Mappable(Protocol[_ValueType]):
    """
    Allows to chain wrapped values with regular functions.

    Behaves like functor.
    """

    def map(  # noqa: A003
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'Mappable[_NewValueType]':
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Is the opposite of :meth:`Fixable.fix`.
        """


@runtime
class Fixable(Protocol[_ValueType, _ErrorType]):
    """Represents containers that can be fixed and rescued."""

    def fix(
        self, function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Fixable[_NewValueType, _ErrorType]':
        """
        Applies 'function' to the error and transforms failure to success.

        And returns a new functor value.
        Works for containers that represent failure.
        Is the opposite of :meth:`Mappable.map`.
        """


@runtime
class Rescueable(Protocol[_ValueType, _ErrorType]):
    """
    Represents a "context" in which calculations can be executed.

    ``Rescueable`` allows you to bind together
    a series of calculations while maintaining
    the context of that specific container.
    """

    def rescue(
        self,
        function: Callable[
            [_ErrorType], 'Rescueable[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Rescueable[_NewValueType, _NewErrorType]':
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new container.
        Works for containers that represent failure.
        Is the opposite of :meth:`~bind`.
        """


@runtime
class Unwrapable(Protocol[_ValueType]):
    """Represents containers that can unwrap and return its wrapped value."""

    def value_or(
        self, default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        """Forces to unwrap value from container or return a default."""

    def unwrap(self) -> _ValueType:
        """
        Custom magic method to unwrap inner value from container.

        Should be redefined for ones that actually have values.
        And for ones that raise an exception for no values.

        This method is the opposite of :meth:`~failure`.
        """


@runtime
class UnwrapableFailure(Protocol[_ValueType, _ErrorType]):
    """Allows to unwrap failures."""

    def map_failure(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'Fixable[_ValueType, _NewErrorType]':
        """
        Uses 'function' to transform one error to another.

        And returns a new functor value.
        Works for containers that represent failure.
        Is the opposite of :meth:`~map`.
        """

    def failure(self) -> _ErrorType:
        """
        Custom magic method to unwrap inner value from the failed container.

        This method is the opposite of :meth:`~unwrap`.
        """
