# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, NoReturn, TypeVar

from returns.primitives.exceptions import ImmutableStateError

ValueType = TypeVar('ValueType')
NewValueType = TypeVar('NewValueType')


class _BaseMonad(Generic[ValueType], metaclass=ABCMeta):
    """Utility class to provide all needed magic methods to the contest."""

    __slots__ = ('_inner_value',)
    _inner_value: Any

    def __setattr__(self, attr_name, attr_value) -> NoReturn:
        """Makes inner state of the monads immutable."""
        raise ImmutableStateError()

    def __delattr__(self, attr_name) -> NoReturn:  # noqa: Z434
        """Makes inner state of the monads immutable."""
        raise ImmutableStateError()

    def __str__(self) -> str:
        """Converts to string."""
        return '{0}: {1}'.format(
            self.__class__.__qualname__,
            str(self._inner_value),
        )

    def __eq__(self, other) -> bool:
        """Used to compare two 'Monad' objects."""
        if not isinstance(other, _BaseMonad):
            return False
        if type(self) != type(other):
            return False
        return self._inner_value == other._inner_value  # noqa: Z441


class Monad(_BaseMonad[ValueType]):
    """
    Represents a "context" in which calculations can be executed.

    You won't create 'Monad' instances directly.
    Instead, sub-classes implement specific contexts.
    Monads allow you to bind together
    a series of calculations while maintaining
    the context of that specific monad.

    This is an abstract class with the API declaration.

    Attributes:
        _inner_value: Wrapped internal immutable state.

    """

    @abstractmethod
    def fmap(self, function):  # pragma: no cover
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Works for monads that represent success.
        Is the opposite of :meth:`~efmap`.
        """
        raise NotImplementedError()

    @abstractmethod
    def bind(self, function):  # pragma: no cover
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new monad.
        Works for monads that represent success.
        Is the opposite of :meth:`~ebind`.
        """
        raise NotImplementedError()

    @abstractmethod
    def efmap(self, function):  # pragma: no cover
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        Works for monads that represent failure.
        Is the opposite of :meth:`~fmap`.
        """
        raise NotImplementedError()

    @abstractmethod
    def ebind(self, function):  # pragma: no cover
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
    def unwrap(self) -> ValueType:  # pragma: no cover
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
