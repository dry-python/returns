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

    See also:
        https://github.com/gcanti/fp-ts/blob/master/docs/modules/Option.ts.md

    """

    _inner_value: Optional[_ValueType]

    # These two are required for projects like `classes`:
    success_type: ClassVar[Type['_Some']]
    failure_type: ClassVar[Type['_Nothing']]

    @classmethod
    def new(cls, inner_value: Optional[_ValueType]) -> 'Maybe[_ValueType]':
        """
        Creates new instance of ``Maybe`` container based on a value.

        .. code:: python

          >>> from returns.maybe import Maybe, Some, Nothing
          >>> assert Maybe.new(1) == Some(1)
          >>> assert Maybe.new(None) == Nothing

        """
        if inner_value is None:
            return _Nothing(inner_value)
        return _Some(inner_value)

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.maybe import Some, Nothing
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Some('a').map(mappable) == Some('ab')
          >>> assert Nothing.map(mappable) == Nothing

        """
        raise NotImplementedError

    def bind(
        self,
        function: Callable[[_ValueType], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.maybe import Nothing, Maybe, Some
          >>> def bindable(string: str) -> Maybe[str]:
          ...      return Some(string + 'b')
          ...
          >>> assert Some('a').bind(bindable) == Some('ab')
          >>> assert Nothing.bind(bindable) == Nothing

        """
        raise NotImplementedError

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        """
        Get value from succesful container or default value from failed one.

        .. code:: python

          >>> from returns.maybe import Nothing, Some
          >>> assert Some(0).value_or(1) == 0
          >>> assert Nothing.value_or(1) == 1

        """
        raise NotImplementedError

    def unwrap(self) -> _ValueType:
        """
        Get value from successful container or raise exception for failed one.

        .. code:: python

          >>> from returns.maybe import Nothing, Some
          >>> assert Some(1).unwrap() == 1

        .. code::

          >>> Nothing.unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise NotImplementedError

    def failure(self) -> None:
        """
        Get failed value from failed container or raise exception from success.

        .. code:: python

          >>> from returns.maybe import Nothing, Some
          >>> assert Nothing.failure() is None

        .. code::

          >>> Some(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
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

          >>> from returns.maybe import Maybe, Nothing, Some
          >>> def example(argument: int) -> float:
          ...     return argument / 2
          ...
          >>> assert Maybe.lift(example)(Some(2)) == Some(1.0)
          >>> assert Maybe.lift(example)(Nothing) == Nothing

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
        Private contructor for ``_Nothing`` type.

        Use :attr:`~Nothing` instead.
        Wraps the given value in the ``_Nothing`` container.

        ``inner_value`` can only be ``None``.
        """
        super().__init__(None)

    def __str__(self):
        """Custom ``str`` definition without the state inside."""
        return '<Nothing>'

    def map(self, function):  # noqa: A003
        """Does nothing for ``Nothing``."""
        return self

    def bind(self, function):
        """Does nothing for ``Nothing``."""
        return self

    def value_or(self, default_value):
        """Returns default value."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self) -> None:
        """Returns failed value."""
        return self._inner_value


@final
class _Some(Maybe[_ValueType]):
    """
    Represents a calculation which has succeeded and contains the value.

    Quite similar to ``Success`` type.
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """
        Private type constructor.

        Please, use :func:`~Some` instead.
        Required for typing.
        """
        super().__init__(inner_value)

    def map(self, function):  # noqa: A003
        """Composes current container with a pure function."""
        return Maybe.new(function(self._inner_value))

    def bind(self, function):
        """Binds current container to a function that returns container."""
        return function(self._inner_value)

    def value_or(self, default_value):
        """Returns inner value for successful container."""
        return self._inner_value

    def unwrap(self):
        """Returns inner value for successful container."""
        return self._inner_value

    def failure(self):
        """Raises exception for succesful container."""
        raise UnwrapFailedError(self)


Maybe.success_type = _Some
Maybe.failure_type = _Nothing


def Some(inner_value: Optional[_ValueType]) -> Maybe[_ValueType]:  # noqa: N802
    """
    Public unit function of protected :class:`~_Some` type.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> str(Some(1))
      '<Some: 1>'
      >>> assert Some(None) == Nothing

    """
    return Maybe.new(inner_value)


#: Public unit value of protected :class:`~_Nothing` type.
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
