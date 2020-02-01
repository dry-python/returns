# -*- coding: utf-8 -*-

from typing import Any, Callable, TypeVar, Union

from typing_extensions import Protocol, runtime

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')


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
        Is the opposite of :meth:`~Rescueable.rescue`.
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
        Is the opposite of :meth:`~Fixable.fix`.
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
        Is the opposite of :meth:`~Mappable.map`.
        """


@runtime
class Rescueable(Protocol[_NewValueType, _ErrorType]):
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
        Is the opposite of :meth:`~Bindable.bind`.
        """


@runtime
class Unwrapable(Protocol[_ValueType, _ErrorType]):
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

        This method is the opposite of :meth:`~Unwrapable.failure`.
        """

    def failure(self) -> _ErrorType:
        """
        Custom magic method to unwrap inner value from the failed container.

        This method is the opposite of :meth:`~Unwrapable.unwrap`.
        """


@runtime
class Altable(Protocol[_ValueType, _ErrorType]):
    """Allows to unwrap failures."""

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'Fixable[_ValueType, _NewErrorType]':
        """
        Uses 'function' to transform one error to another.

        And returns a new functor value.
        Works for containers that represent failure.
        Is the opposite of :meth:`~Mappable.map`.
        """


@runtime
class Instanceable(Protocol[_ValueType]):
    """
    Allows to create unit containers from raw values.

    This is heavily related to classes that do not have conunter-parts.
    Like ``IO`` and ``RequiresContext``.
    """

    @classmethod
    def from_value(
        cls, inner_value: _NewValueType,
    ) -> 'Unitable[_NewValueType, Any]':
        """This method is required to create new containers."""


@runtime
class Unitable(Protocol[_ValueType, _ErrorType]):
    """
    Allows to create unit values from success and failure.

    This is heavily ``Result`` related class.
    """

    @classmethod
    def from_success(
        cls, inner_value: _NewValueType,
    ) -> 'Unitable[_NewValueType, Any]':
        """This method is required to create values that represent success."""

    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType,
    ) -> 'Unitable[Any, _NewErrorType]':
        """This method is required to create values that represent failure."""
