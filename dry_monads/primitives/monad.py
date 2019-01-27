# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar

ValueType = TypeVar('ValueType')
NewValueType = TypeVar('NewValueType')


class Monad(Generic[ValueType], metaclass=ABCMeta):
    """
    Represents a "context" in which calculations can be executed.

    You won't create 'Monad' instances directly.
    Instead, sub-classes implement specific contexts.
    Monads allow you to bind together
    a series of calculations while maintaining
    the context of that specific monad.

    """

    _inner_value: Any

    @abstractmethod
    def fmap(self, function):  # pragma: no cover
        """
        Applies 'function' to the contents of the functor.

        And returns a new functor value.
        """
        raise NotImplementedError()

    @abstractmethod
    def bind(self, function):  # pragma: no cover
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new monad.
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
        """
        raise NotImplementedError()

    def __str__(self) -> str:
        """Converts to string."""
        return '{0}: {1}'.format(
            self.__class__.__qualname__,
            str(self._inner_value),
        )

    def __eq__(self, other) -> bool:
        """Used to compare two 'Monad' objects."""
        if not isinstance(other, Monad):
            return False
        return self._inner_value == other._inner_value  # noqa: Z441
