from abc import ABCMeta
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns.interfaces.specific.maybe import MaybeBased2
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.hkt import Kind1, SupportsKind1

# Definitions:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


class Maybe(
    BaseContainer,
    SupportsKind1['Maybe', _ValueType],
    MaybeBased2[_ValueType, None],
    metaclass=ABCMeta,
):
    """
    Represents a result of a series of computations that can return ``None``.

    An alternative to using exceptions or constant ``is None`` checks.
    ``Maybe`` is an abstract type and should not be instantiated directly.
    Instead use ``Some`` and ``Nothing``.

    See also:
        - https://github.com/gcanti/fp-ts/blob/master/docs/modules/Option.ts.md

    """

    _inner_value: Optional[_ValueType]
    __match_args__ = ('_inner_value',)

    #: Alias for `Nothing`
    empty: ClassVar['Maybe[Any]']

    # These two are required for projects like `classes`:

    #: Success type that is used to represent the successful computation.
    success_type: ClassVar[Type['Some']]
    #: Failure type that is used to represent the failed computation.
    failure_type: ClassVar[Type['_Nothing']]

    #: Typesafe equality comparison with other `Result` objects.
    equals = container_equality

    def map(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Maybe[_NewValueType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.maybe import Some, Nothing
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'

          >>> assert Some('a').map(mappable) == Some('ab')
          >>> assert Nothing.map(mappable) == Nothing

        """

    def apply(
        self,
        function: Kind1['Maybe', Callable[[_ValueType], _NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.maybe import Some, Nothing

          >>> def appliable(string: str) -> str:
          ...      return string + 'b'

          >>> assert Some('a').apply(Some(appliable)) == Some('ab')
          >>> assert Some('a').apply(Nothing) == Nothing
          >>> assert Nothing.apply(Some(appliable)) == Nothing
          >>> assert Nothing.apply(Nothing) == Nothing

        """

    def bind(
        self,
        function: Callable[[_ValueType], Kind1['Maybe', _NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.maybe import Nothing, Maybe, Some
          >>> def bindable(string: str) -> Maybe[str]:
          ...      return Some(string + 'b')

          >>> assert Some('a').bind(bindable) == Some('ab')
          >>> assert Nothing.bind(bindable) == Nothing

        """

    def bind_optional(
        self,
        function: Callable[[_ValueType], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        """
        Binds a function returning an optional value over a container.

        .. code:: python

          >>> from returns.maybe import Some, Nothing
          >>> from typing import Optional

          >>> def bindable(arg: str) -> Optional[int]:
          ...     return len(arg) if arg else None

          >>> assert Some('a').bind_optional(bindable) == Some(1)
          >>> assert Some('').bind_optional(bindable) == Nothing

        """

    def lash(
        self,
        function: Callable[[Any], Kind1['Maybe', _ValueType]],
    ) -> 'Maybe[_ValueType]':
        """
        Composes failed container with a function that returns a container.

        .. code:: python

          >>> from returns.maybe import Maybe, Some, Nothing

          >>> def lashable(arg=None) -> Maybe[str]:
          ...      return Some('b')

          >>> assert Some('a').lash(lashable) == Some('a')
          >>> assert Nothing.lash(lashable) == Some('b')

        We need this feature to make ``Maybe`` compatible
        with different ``Result`` like operations.

        """

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        """
        Get value from successful container or default value from failed one.

        .. code:: python

          >>> from returns.maybe import Nothing, Some
          >>> assert Some(0).value_or(1) == 0
          >>> assert Nothing.value_or(1) == 1

        """

    def or_else_call(
        self,
        function: Callable[[], _NewValueType],
    ) -> Union[_ValueType, _NewValueType]:
        """
        Get value from successful container or default value from failed one.

        Really close to :meth:`~Maybe.value_or` but works with lazy values.
        This method is unique to ``Maybe`` container, because other containers
        do have ``.alt`` method.

        But, ``Maybe`` does not have this method.
        There's nothing to ``alt`` in ``Nothing``.

        Instead, it has this method to execute
        some function if called on a failed container:

        .. code:: pycon

          >>> from returns.maybe import Some, Nothing
          >>> assert Some(1).or_else_call(lambda: 2) == 1
          >>> assert Nothing.or_else_call(lambda: 2) == 2

        It might be useful to work with exceptions as well:

        .. code:: pycon

          >>> def fallback() -> NoReturn:
          ...    raise ValueError('Nothing!')

          >>> Nothing.or_else_call(fallback)
          Traceback (most recent call last):
            ...
          ValueError: Nothing!

        """

    def unwrap(self) -> _ValueType:
        """
        Get value from successful container or raise exception for failed one.

        .. code:: pycon
          :force:

          >>> from returns.maybe import Nothing, Some
          >>> assert Some(1).unwrap() == 1

          >>> Nothing.unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """  # noqa: RST307

    def failure(self) -> None:
        """
        Get failed value from failed container or raise exception from success.

        .. code:: pycon
          :force:

          >>> from returns.maybe import Nothing, Some
          >>> assert Nothing.failure() is None

          >>> Some(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """  # noqa: RST307

    @classmethod
    def from_value(
        cls, inner_value: _NewValueType,
    ) -> 'Maybe[_NewValueType]':
        """
        Creates new instance of ``Maybe`` container based on a value.

        .. code:: python

          >>> from returns.maybe import Maybe, Some
          >>> assert Maybe.from_value(1) == Some(1)
          >>> assert Maybe.from_value(None) == Some(None)

        """
        return Some(inner_value)

    @classmethod
    def from_optional(
        cls, inner_value: Optional[_NewValueType],
    ) -> 'Maybe[_NewValueType]':
        """
        Creates new instance of ``Maybe`` container based on an optional value.

        .. code:: python

          >>> from returns.maybe import Maybe, Some, Nothing
          >>> assert Maybe.from_optional(1) == Some(1)
          >>> assert Maybe.from_optional(None) == Nothing

        """
        if inner_value is None:
            return _Nothing(inner_value)
        return Some(inner_value)


@final
class _Nothing(Maybe[Any]):
    """Represents an empty state."""

    _inner_value: None
    _instance: Optional['_Nothing'] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> '_Nothing':
        if cls._instance is None:
            cls._instance = object.__new__(cls)  # noqa: WPS609
        return cls._instance

    def __init__(self, inner_value: None = None) -> None:  # noqa: WPS632
        """
        Private constructor for ``_Nothing`` type.

        Use :attr:`~Nothing` instead.
        Wraps the given value in the ``_Nothing`` container.

        ``inner_value`` can only be ``None``.
        """
        super().__init__(None)

    def __repr__(self):
        """
        Custom ``str`` definition without the state inside.

        .. code:: python

          >>> from returns.maybe import Nothing
          >>> assert str(Nothing) == '<Nothing>'
          >>> assert repr(Nothing) == '<Nothing>'

        """
        return '<Nothing>'

    def map(self, function):
        """Does nothing for ``Nothing``."""
        return self

    def apply(self, container):
        """Does nothing for ``Nothing``."""
        return self

    def bind(self, function):
        """Does nothing for ``Nothing``."""
        return self

    def bind_optional(self, function):
        """Does nothing."""
        return self

    def lash(self, function):
        """Composes this container with a function returning container."""
        return function(None)

    def value_or(self, default_value):
        """Returns default value."""
        return default_value

    def or_else_call(self, function):
        """Returns the result of a passed function."""
        return function()

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        raise UnwrapFailedError(self)

    def failure(self) -> None:
        """Returns failed value."""
        return self._inner_value


@final
class Some(Maybe[_ValueType]):
    """
    Represents a calculation which has succeeded and contains the value.

    Quite similar to ``Success`` type.
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Some constructor."""
        super().__init__(inner_value)

    if not TYPE_CHECKING:  # noqa: WPS604  # pragma: no branch
        def bind(self, function):
            """Binds current container to a function that returns container."""
            return function(self._inner_value)

        def bind_optional(self, function):
            """Binds a function returning an optional value over a container."""
            return Maybe.from_optional(function(self._inner_value))

        def unwrap(self):
            """Returns inner value for successful container."""
            return self._inner_value

    def map(self, function):
        """Composes current container with a pure function."""
        return Some(function(self._inner_value))

    def apply(self, container):
        """Calls a wrapped function in a container on this container."""
        if isinstance(container, self.success_type):
            return self.map(container.unwrap())  # type: ignore
        return container

    def lash(self, function):
        """Does nothing for ``Some``."""
        return self

    def value_or(self, default_value):
        """Returns inner value for successful container."""
        return self._inner_value

    def or_else_call(self, function):
        """Returns inner value for successful container."""
        return self._inner_value

    def failure(self):
        """Raises exception for successful container."""
        raise UnwrapFailedError(self)


Maybe.success_type = Some
Maybe.failure_type = _Nothing

#: Public unit value of protected :class:`~_Nothing` type.
Nothing: Maybe[NoReturn] = _Nothing()
Maybe.empty = Nothing


def maybe(
    function: Callable[..., Optional[_ValueType]],
) -> Callable[..., Maybe[_ValueType]]:
    """
    Decorator to convert ``None``-returning function to ``Maybe`` container.

    This decorator works with sync functions only. Example:

    .. code:: python

      >>> from typing import Optional
      >>> from returns.maybe import Nothing, Some, maybe

      >>> @maybe
      ... def might_be_none(arg: int) -> Optional[int]:
      ...     if arg == 0:
      ...         return None
      ...     return 1 / arg

      >>> assert might_be_none(0) == Nothing
      >>> assert might_be_none(1) == Some(1.0)

    Requires our :ref:`mypy plugin <mypy-plugins>`.

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        return Maybe.from_optional(function(*args, **kwargs))
    return decorator
