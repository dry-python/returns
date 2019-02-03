# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from returns.primitives.exceptions import ImmutableStateError

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


class _BaseContainer(object, metaclass=ABCMeta):
    """Utility class to provide all needed magic methods to the contest."""

    __slots__ = ('_inner_value',)

    def __init__(self, inner_value):
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)

    def __setattr__(self, attr_name, attr_value):
        """Makes inner state of the monads immutable."""
        raise ImmutableStateError()

    def __delattr__(self, attr_name):  # noqa: Z434
        """Makes inner state of the monads immutable."""
        raise ImmutableStateError()

    def __str__(self):
        """Converts to string."""
        return '{0}: {1}'.format(
            self.__class__.__qualname__,
            str(self._inner_value),
        )

    def __eq__(self, other):
        """Used to compare two 'Container' objects."""
        if not isinstance(other, _BaseContainer):
            return False
        if type(self) != type(other):
            return False
        return self._inner_value == other._inner_value  # noqa: Z441


class Container(_BaseContainer, metaclass=ABCMeta):
    """
    Represents a "context" in which calculations can be executed.

    You won't create 'Container' instances directly.
    Instead, sub-classes implement specific contexts.
    Monads allow you to bind together
    a series of calculations while maintaining
    the context of that specific monad.

    This is an abstract class with the API declaration.

    Attributes:
        _inner_value: Wrapped internal immutable state.

    """

    @abstractmethod  # noqa: A003
    def map(self, function):  # pragma: no cover
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Works for monads that represent success.
        Is the opposite of :meth:`~fix`.
        """
        raise NotImplementedError()

    @abstractmethod
    def bind(self, function):  # pragma: no cover
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new monad.
        Works for monads that represent success.
        Is the opposite of :meth:`~rescue`.
        """
        raise NotImplementedError()

    @abstractmethod
    def fix(self, function):  # pragma: no cover
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Works for monads that represent failure.
        Is the opposite of :meth:`~map`.
        """
        raise NotImplementedError()

    @abstractmethod
    def rescue(self, function):  # pragma: no cover
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new monad.
        Works for monads that represent failure.
        Is the opposite of :meth:`~bind`.
        """
        raise NotImplementedError()

    @abstractmethod
    def value_or(self, default_value):  # pragma: no cover
        """Forces to unwrap value from monad or return a default."""
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self):  # pragma: no cover
        """
        Custom magic method to unwrap inner value from monad.

        Should be redefined for ones that actually have values.
        And for ones that raise an exception for no values.

        This method is the opposite of :meth:`~failure`.
        """
        raise NotImplementedError()

    @abstractmethod
    def failure(self):  # pragma: no cover
        """
        Custom magic method to unwrap inner value from the failed monad.

        This method is the opposite of :meth:`~unwrap`.
        """
        raise NotImplementedError()


class GenericContainerOneSlot(Generic[_ValueType], Container):
    """
    Base class for monads with one typed slot.

    Use this type for generic inheritance only.
    Use :class:`~Container` as a general type for polymorphism.
    """


class GenericContainerTwoSlots(Generic[_ValueType, _ErrorType], Container):
    """
    Base class for monads with two typed slot.

    Use this type for generic inheritance only.
    Use :class:`~Container` as a general type for polymorphism.
    """
