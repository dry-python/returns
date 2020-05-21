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
class Unifiable(Protocol[_ValueType, _ErrorType]):
    """
    Represents a "context" in which calculations can be executed.

    ``Unifiable`` allows you to bind together
    a series of calculations while maintaining
    the context of that specific container.

    As the name suggests is used to unify error types
    while binding the value type.
    """

    def unify(
        self,
        function: Callable[
            [_ValueType],
            'Unifiable[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Unifiable[_NewValueType, Union[_ErrorType, _NewErrorType]]':
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new container.
        Works for containers that represent success.
        Works the same way as :meth:`~Bindable.bind`,
        but has different type semantics.
        Is the opposite of :meth:`~Rescueable.rescue`.
        """


@runtime
class Mappable(Protocol[_ValueType]):
    """
    Allows to chain wrapped values with regular functions.

    Behaves like a functor.

    See also:
        https://en.wikipedia.org/wiki/Functor

    """

    def map(  # noqa: WPS125
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'Mappable[_NewValueType]':
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Is the opposite of :meth:`~Fixable.fix`.

        Has :func:`returns.pointfree.map` helper with the inverse semantic.
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
class Applicative(Protocol[_ValueType]):
    """
    Allows to create unit containers from raw values.

    All containers should support this interface.

    See also:
        https://en.wikipedia.org/wiki/Applicative_functor
        http://learnyouahaskell.com/functors-applicative-functors-and-monoids

    """

    @classmethod
    def from_value(
        cls, inner_value: _NewValueType,
    ) -> 'Unitable[_NewValueType, Any]':
        """This method is required to create new containers."""

    def apply(
        self,
        container: 'Applicative[Callable[[_ValueType], _NewValueType]]',
    ) -> 'Applicative[_NewValueType]':
        """Calls a wrapped function in a container on this container."""


@runtime
class Unitable(Applicative[_ValueType], Protocol[_ValueType, _ErrorType]):
    """
    Allows to create unit values from success and failure.

    This is a heavily ``Result``-related class.
    """

    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType,
    ) -> 'Unitable[Any, _NewErrorType]':
        """This method is required to create values that represent failure."""
