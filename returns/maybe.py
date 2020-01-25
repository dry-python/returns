# -*- coding: utf-8 -*-

from abc import ABCMeta
from functools import wraps
from inspect import iscoroutinefunction
from typing import (
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Generic,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import final

from returns.primitives.container import BaseContainer
from returns.primitives.exceptions import UnwrapFailedError

# Definitions:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


class Maybe(
    BaseContainer,
    Generic[_ValueType],
    metaclass=ABCMeta,
):
    """
    Represents a result of a series of commutation that can return ``None``.

    An alternative to using exceptions or constant ``is None`` checks.
    ``Maybe`` is an abstract type and should not be instantiated directly.
    Instead use ``Some`` and ``Nothing``.
    """

    _inner_value: Optional[_ValueType]

    # These two are required for projects like `classes`:
    success_type: ClassVar[Type['_Some']]
    failure_type: ClassVar[Type['_Nothing']]

    @classmethod
    def new(cls, inner_value: Optional[_ValueType]) -> 'Maybe[_ValueType]':
        """Creates new instance of Maybe container based on a value."""
        if inner_value is None:
            return _Nothing(inner_value)
        return _Some(inner_value)

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """Abstract method to compose container with a pure function."""
        raise NotImplementedError

    def bind(
        self,
        function: Callable[[_ValueType], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':
        """Abstract method to compose container with other container."""
        raise NotImplementedError

    def fix(
        self,
        function: Callable[[None], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """Abstract method to compose container with a pure function."""
        raise NotImplementedError

    def rescue(
        self,
        function: Callable[[None], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':
        """Abstract method to compose container with other container."""
        raise NotImplementedError

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        """Get value or default value."""
        raise NotImplementedError

    def unwrap(self) -> _ValueType:
        """Get value or raise exception."""
        raise NotImplementedError

    def failure(self) -> None:
        """Get failed value or raise exception."""
        raise NotImplementedError

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[['Maybe[_ValueType]'], 'Maybe[_NewValueType]']:
        """
        Lifts function to be wrapped in ``Maybe`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to: ``Maybe[a] -> Maybe[b]``

        Works similar to :meth:`~Maybe.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.maybe import Maybe
          >>> def example(argument: int) -> float:
          ...     return argument / 2
          ...
          >>> assert Maybe.lift(example)(Maybe.new(2)) == Maybe.new(1.0)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)


@final
class _Nothing(Maybe[Any]):
    """Represents an empty state."""

    _inner_value: None

    def __init__(self, inner_value: None = None) -> None:
        """
        Wraps the given value in the ``Nothing`` container.

        ``inner_value`` can only be ``None``.
        """
        super().__init__(None)

    def __str__(self):
        """Custom ``str`` definition without the state inside."""
        return '<Nothing>'

    def map(self, function):  # noqa: A003
        """
        Returns the 'Nothing' instance that was used to call the method.

        .. code:: python

          >>> from returns.maybe import Nothing
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Nothing.map(mappable) == Nothing

        """
        return self

    def bind(self, function):
        """
        Returns the 'Nothing' instance that was used to call the method.

        .. code:: python

          >>> from returns.maybe import Nothing, Maybe, Some
          >>> def bindable(string: str) -> Maybe[str]:
          ...      return Some(string + 'b')
          ...
          >>> assert Nothing.bind(bindable) == Nothing

        """
        return self

    def fix(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Some' object containing the result.
        'function' should not accept one argument
        and return a non-container result.

        .. code:: python

          >>> from returns.maybe import Nothing, Some
          >>> def fixable(_state) -> str:
          ...      return 'ab'
          ...
          >>> assert Nothing.fix(fixable) == Some('ab')

        """
        return Maybe.new(function(self._inner_value))

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept one argument
        and return a container result: 'Nothing' or 'Some' type object.

        .. code:: python

          >>> from returns.maybe import Nothing, Maybe, Some
          >>> def rescuable(_state) -> Maybe[str]:
          ...      return Some('ab')
          ...
          >>> assert Nothing.rescue(rescuable) == Some('ab')

        """
        return function(self._inner_value)

    def value_or(self, default_value):
        """
        Returns the value if we deal with 'Some' or default if 'Nothing'.

        .. code:: python

          >>> from returns.maybe import Nothing
          >>> Nothing.value_or(1)
          1

        """
        return default_value

    def unwrap(self):
        """
        Raises an exception, since it does not have a value inside.

        .. code:: python

          >>> from returns.maybe import Nothing
          >>> Nothing.unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise UnwrapFailedError(self)

    def failure(self) -> None:
        """
        Get failed value.

        .. code:: python

          >>> from returns.maybe import Nothing
          >>> assert Nothing.failure() is None

        """
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
        super().__init__(inner_value)

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the 'Some' instance
        and returns a new 'Maybe' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> from returns.maybe import Some
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Some('a').map(mappable) == Some('ab')

        """
        return Maybe.new(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return 'Nothing' or 'Some' type object.

        .. code:: python

          >>> from returns.maybe import Maybe, Some
          >>> def bindable(string: str) -> Maybe[str]:
          ...      return Some(string + 'b')
          ...
          >>> assert Some('a').bind(bindable) == Some('ab')

        """
        return function(self._inner_value)

    def fix(self, function):
        """
        Returns the 'Some' instance that was used to call the method.

        .. code:: python

          >>> from returns.maybe import Some
          >>> def fixable(_state) -> str:
          ...      return 'ab'
          ...
          >>> assert Some('a').fix(fixable) == Some('a')

        """
        return self

    def rescue(self, function):
        """
        Returns the 'Some' instance that was used to call the method.

        .. code:: python

          >>> from returns.maybe import Maybe, Some
          >>> def rescuable(_state) -> Maybe[str]:
          ...      return Some('ab')
          ...
          >>> assert Some('a').rescue(rescuable) == Some('a')

        """
        return self

    def value_or(self, default_value):
        """
        Returns the value if we deal with 'Some' or default if 'Nothing'.

        .. code:: python

          >>> from returns.maybe import Some
          >>> Some(1).value_or(2)
          1

        """
        return self._inner_value

    def unwrap(self):
        """
        Returns the unwrapped value from the inside of this container.

        .. code:: python

          >>> from returns.maybe import Some
          >>> Some(1).unwrap()
          1

        """
        return self._inner_value

    def failure(self):
        """
        Raises an exception, since it does not have a failure inside.

        .. code:: python

          >>> from returns.maybe import Some
          >>> Some(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise UnwrapFailedError(self)


Maybe.success_type = _Some
Maybe.failure_type = _Nothing


def Some(inner_value: Optional[_ValueType]) -> Maybe[_ValueType]:  # noqa: N802
    """
    Public unit function of protected `_Some` type.

    .. code:: python

      >>> from returns.maybe import Some
      >>> str(Some(1))
      '<Some: 1>'

    """
    return Maybe.new(inner_value)


#: Public unit value of protected `_Nothing` type.
Nothing: Maybe[NoReturn] = _Nothing()


@overload
def maybe(  # type: ignore
    function: Callable[
        ...,
        Coroutine[_FirstType, _SecondType, Optional[_ValueType]],
    ],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, Maybe[_ValueType]],
]:
    """Case for async functions."""


@overload
def maybe(
    function: Callable[..., Optional[_ValueType]],
) -> Callable[..., Maybe[_ValueType]]:
    """Case for regular functions."""


def maybe(function):
    """
    Decorator to covert ``None`` returning function to ``Maybe`` container.

    Supports both async and regular functions.

    .. code:: python

      >>> from typing import Optional
      >>> from returns.maybe import Nothing, Some, maybe

      >>> @maybe
      ... def might_be_none(arg: int) -> Optional[int]:
      ...     if arg == 0:
      ...         return None
      ...     return 1 / arg
      ...
      >>> assert might_be_none(0) == Nothing
      >>> assert might_be_none(1) == Some(1.0)

    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):  # noqa: WPS430
            regular_result = await function(*args, **kwargs)
            if regular_result is None:
                return Nothing
            return Some(regular_result)
    else:
        def decorator(*args, **kwargs):  # noqa: WPS430
            regular_result = function(*args, **kwargs)
            if regular_result is None:
                return Nothing
            return Some(regular_result)
    return wraps(function)(decorator)
