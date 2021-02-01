from functools import wraps
from typing import TYPE_CHECKING, Callable, TypeVar

from typing_extensions import final

from returns.interfaces.specific import io
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.hkt import Kind1, SupportsKind1, dekind

if TYPE_CHECKING:
    from returns.io.ioresult import IOResult

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Result related:
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(
    BaseContainer,
    SupportsKind1['IO', _ValueType],
    io.IOLike1[_ValueType],
):
    """
    Explicit container for impure function results.

    We also sometimes call it "marker" since once it is marked,
    it cannot be ever unmarked.
    There's no way to directly get its internal value.

    Note that ``IO`` represents a computation that never fails.

    Examples of such computations are:

    - read / write to localStorage
    - get the current time
    - write to the console
    - get a random number

    Use ``IOResult[...]`` for operations that might fail.
    Like DB access or network operations.

    See also:
        - https://dev.to/gcanti/getting-started-with-fp-ts-io-36p6
        - https://gist.github.com/chris-taylor/4745921

    """

    _inner_value: _ValueType

    #: Typesafe equality comparison with other `Result` objects.
    equals = container_equality

    def __init__(self, inner_value: _ValueType) -> None:
        """
        Public constructor for this type. Also required for typing.

        .. code:: python

          >>> from returns.io import IO
          >>> assert str(IO(1)) == '<IO: 1>'

        """
        super().__init__(inner_value)

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'IO[_NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the IO instance
        and returns a new IO object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> def mappable(string: str) -> str:
          ...      return string + 'b'

          >>> assert IO('a').map(mappable) == IO('ab')

        """
        return IO(function(self._inner_value))

    def apply(
        self,
        container: Kind1['IO', Callable[[_ValueType], _NewValueType]],
    ) -> 'IO[_NewValueType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.io import IO
          >>> assert IO('a').apply(IO(lambda inner: inner + 'b')) == IO('ab')

        Or more complex example that shows how we can work
        with regular functions and multiple ``IO`` arguments:

        .. code:: python

          >>> from returns.curry import curry

          >>> @curry
          ... def appliable(first: str, second: str) -> str:
          ...      return first + second

          >>> assert IO('b').apply(IO('a').apply(IO(appliable))) == IO('ab')

        """
        return self.map(dekind(container)._inner_value)  # noqa: WPS437

    def bind(
        self,
        function: Callable[[_ValueType], Kind1['IO', _NewValueType]],
    ) -> 'IO[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return ``IO`` type object.

        .. code:: python

          >>> def bindable(string: str) -> IO[str]:
          ...      return IO(string + 'b')

          >>> assert IO('a').bind(bindable) == IO('ab')

        """
        return dekind(function(self._inner_value))

    #: Alias for `bind` method. Part of the `IOLikeN` interface.
    bind_io = bind

    @classmethod
    def from_value(cls, inner_value: _NewValueType) -> 'IO[_NewValueType]':
        """
        Unit function to construct new ``IO`` values.

        Is the same as regular constructor:

        .. code:: python

          >>> from returns.io import IO
          >>> assert IO(1) == IO.from_value(1)

        Part of the :class:`returns.interfaces.applicative.ApplicativeN`
        interface.
        """
        return IO(inner_value)

    @classmethod
    def from_io(cls, inner_value: 'IO[_NewValueType]') -> 'IO[_NewValueType]':
        """
        Unit function to construct new ``IO`` values from existing ``IO``.

        .. code:: python

          >>> from returns.io import IO
          >>> assert IO(1) == IO.from_io(IO(1))

        Part of the :class:`returns.interfaces.specific.IO.IOLikeN` interface.

        """
        return inner_value

    @classmethod
    def from_ioresult(
        cls,
        inner_value: 'IOResult[_NewValueType, _NewErrorType]',
    ) -> 'IO[Result[_NewValueType, _NewErrorType]]':
        """
        Converts ``IOResult[a, b]`` back to ``IO[Result[a, b]]``.

        Can be really helpful for composition.

        .. code:: python

            >>> from returns.io import IO, IOSuccess
            >>> from returns.result import Success
            >>> assert IO.from_ioresult(IOSuccess(1)) == IO(Success(1))

        Is the reverse of :meth:`returns.io.IOResult.from_typecast`.
        """
        return IO(inner_value._inner_value)  # noqa: WPS437


# Helper functions:

def impure(
    function: Callable[..., _NewValueType],
) -> Callable[..., IO[_NewValueType]]:
    """
    Decorator to mark function that it returns :class:`~IO` container.

    If you need to mark ``async`` function as impure,
    use :func:`returns.future.future` instead.
    This decorator only works with sync functions. Example:

    .. code:: python

      >>> from returns.io import IO, impure

      >>> @impure
      ... def function(arg: int) -> int:
      ...     return arg + 1  # this action is pure, just an example
      ...

      >>> assert function(1) == IO(2)

    Requires our :ref:`mypy plugin <mypy-plugins>`.

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        return IO(function(*args, **kwargs))
    return decorator
