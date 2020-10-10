from abc import ABCMeta
from functools import wraps
from inspect import FrameInfo
from typing import (
    Any,
    Callable,
    ClassVar,
    List,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns.interfaces.specific import result
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.exceptions import UnwrapFailedError
from returns.primitives.hkt import Kind2, SupportsKind2

# Definitions:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


class Result(
    BaseContainer,
    SupportsKind2['Result', _ValueType, _ErrorType],
    result.ResultBased2[_ValueType, _ErrorType],
    metaclass=ABCMeta,
):
    """
    Base class for :class:`~_Failure` and :class:`~_Success`.

    :class:`~Result` does not have a public constructor.
    Use :func:`~Success` and :func:`~Failure` to construct the needed values.

    See also:
        - https://bit.ly/361qQhi
        - https://hackernoon.com/the-throw-keyword-was-a-mistake-l9e532di

    """

    __slots__ = ('_trace',)

    _inner_value: Union[_ValueType, _ErrorType]
    _trace: Optional[List[FrameInfo]]

    # These two are required for projects like `classes`:
    #: Success type that is used to represent the successful computation.
    success_type: ClassVar[Type['_Success']]
    #: Failure type that is used to represent the failed computation.
    failure_type: ClassVar[Type['_Failure']]

    #: Typesafe equality comparison with other `Result` objects.
    equals = container_equality

    @property
    def trace(self) -> Optional[List[FrameInfo]]:
        """Returns a list with stack trace when :func:`~Failure` was called."""
        return self._trace

    def swap(self) -> 'Result[_ErrorType, _ValueType]':
        """
        Swaps value and error types.

        So, values become errors and errors become values.
        It is useful when you have to work with errors a lot.
        And since we have a lot of ``.bind_`` related methods
        and only a single ``.lash`` - it is easier to work with values.

        .. code:: python

          >>> from returns.result import Success, Failure
          >>> assert Success(1).swap() == Failure(1)
          >>> assert Failure(1).swap() == Success(1)

        """

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.result import Failure, Success

          >>> def mappable(string: str) -> str:
          ...      return string + 'b'

          >>> assert Success('a').map(mappable) == Success('ab')
          >>> assert Failure('a').map(mappable) == Failure('a')

        """

    def apply(
        self,
        container: Kind2[
            'Result',
            Callable[[_ValueType], _NewValueType],
            _ErrorType,
        ],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.result import Failure, Success

          >>> def appliable(string: str) -> str:
          ...      return string + 'b'

          >>> assert Success('a').apply(Success(appliable)) == Success('ab')
          >>> assert Failure('a').apply(Success(appliable)) == Failure('a')

          >>> assert Success('a').apply(Failure(1)) == Failure(1)
          >>> assert Failure(1).apply(Failure(2)) == Failure(1)

        """

    def bind(
        self,
        function: Callable[
            [_ValueType],
            Kind2['Result', _NewValueType, _ErrorType],
        ],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.result import Result, Success, Failure

          >>> def bindable(arg: str) -> Result[str, str]:
          ...      if len(arg) > 1:
          ...          return Success(arg + 'b')
          ...      return Failure(arg + 'c')

          >>> assert Success('aa').bind(bindable) == Success('aab')
          >>> assert Success('a').bind(bindable) == Failure('ac')
          >>> assert Failure('a').bind(bindable) == Failure('a')

        """

    #: Alias for `bind_result` method, it is the same as `bind` here.
    bind_result = bind

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function to modify failure.

        .. code:: python

          >>> from returns.result import Failure, Success

          >>> def altable(arg: str) -> str:
          ...      return arg + 'b'

          >>> assert Success('a').alt(altable) == Success('a')
          >>> assert Failure('a').alt(altable) == Failure('ab')

        """

    def lash(
        self,
        function: Callable[
            [_ErrorType], Kind2['Result', _ValueType, _NewErrorType],
        ],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Composes failed container with a function that returns a container.

        .. code:: python

          >>> from returns.result import Result, Success, Failure

          >>> def lashable(arg: str) -> Result[str, str]:
          ...      if len(arg) > 1:
          ...          return Success(arg + 'b')
          ...      return Failure(arg + 'c')

          >>> assert Success('a').lash(lashable) == Success('a')
          >>> assert Failure('a').lash(lashable) == Failure('ac')
          >>> assert Failure('aa').lash(lashable) == Success('aab')

        """

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        """
        Get value or default value.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> assert Success(1).value_or(2) == 1
          >>> assert Failure(1).value_or(2) == 2

        """

    def unwrap(self) -> _ValueType:
        """
        Get value or raise exception.

        .. code:: pycon
          :force:

          >>> from returns.result import Failure, Success
          >>> assert Success(1).unwrap() == 1

          >>> Failure(1).unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """  # noqa: RST399

    def failure(self) -> _ErrorType:
        """
        Get failed value or raise exception.

        .. code:: pycon
          :force:

          >>> from returns.result import Failure, Success
          >>> assert Failure(1).failure() == 1

          >>> Success(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """  # noqa: RST399

    @classmethod
    def from_value(
        cls, inner_value: _NewValueType,
    ) -> 'Result[_NewValueType, Any]':
        """
        One more value to create success unit values.

        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> assert Result.from_value(1) == Success(1)

        You can use this method or :func:`~Success`,
        choose the most convenient for you.

        """
        return Success(inner_value)

    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType,
    ) -> 'Result[Any, _NewErrorType]':
        """
        One more value to create failure unit values.

        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.result import Result, Failure
          >>> assert Result.from_failure(1) == Failure(1)

        You can use this method or :func:`~Failure`,
        choose the most convenient for you.

        """
        return Failure(inner_value)

    @classmethod
    def from_result(
        cls, inner_value: 'Result[_NewValueType, _NewErrorType]',
    ) -> 'Result[_NewValueType, _NewErrorType]':
        """
        Creates a new ``Result`` instance from existing ``Result`` instance.

        .. code:: python

          >>> from returns.result import Result, Failure, Success
          >>> assert Result.from_result(Success(1)) == Success(1)
          >>> assert Result.from_result(Failure(1)) == Failure(1)

        This is a part of
        :class:`returns.interfaces.specific.result.ResultBasedN` interface.
        """
        return inner_value


@final
class _Failure(Result[Any, _ErrorType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    Should not be used directly.

    This is an implementation detail, please, do not use it directly.
    This class only has methods that are logically dependent on the
    current container state: successful or failed.

    Use public data types instead!
    """

    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        """
        Private type constructor.

        Use :func:`~Success` and :func:`~Failure` instead.
        Required for typing.
        """
        super().__init__(inner_value)
        object.__setattr__(self, '_trace', self._get_trace())  # noqa: WPS609

    def swap(self):
        """Failures swap to :class:`_Success`."""
        return _Success(self._inner_value)

    def map(self, function):  # noqa: WPS125
        """Does nothing for ``Failure``."""
        return self

    def apply(self, container):
        """Does nothing for ``Failure``."""
        return self

    def bind(self, function):
        """Does nothing for ``Failure``."""
        return self

    #: Alias for `bind` method. Part of the `ResultBasedN` interface.
    bind_result = bind

    def lash(self, function):
        """Composes this container with a function returning container."""
        return function(self._inner_value)

    def alt(self, function):
        """Composes failed container with a pure function to modify failure."""
        return _Failure(function(self._inner_value))

    def value_or(self, default_value: _NewValueType) -> _NewValueType:
        """Returns default value for failed container."""
        return default_value

    def unwrap(self) -> NoReturn:
        """Raises an exception, since it does not have a value inside."""
        if isinstance(self._inner_value, Exception):
            raise UnwrapFailedError(self) from self._inner_value
        raise UnwrapFailedError(self)

    def failure(self) -> _ErrorType:
        """Returns failed value."""
        return self._inner_value

    def _get_trace(self) -> Optional[List[FrameInfo]]:
        """Method that will be monkey patched when trace is active."""
        return None  # noqa: WPS324


@final
class _Success(Result[_ValueType, Any]):
    """
    Represents a calculation which has succeeded and contains the result.

    Contains the computation value.
    Should not be used directly.

    This is an implementation detail, please, do not use it directly.
    This class only has method that are logically
    dependent on the current container state: successful or failed.

    Use public data types instead!
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """
        Private type constructor.

        Use :func:`~Success` and :func:`~Failure` instead.
        Required for typing.
        """
        super().__init__(inner_value)

    def swap(self):
        """Successes swap to :class:`_Failure`."""
        return _Failure(self._inner_value)

    def map(self, function):  # noqa: WPS125
        """Composes current container with a pure function."""
        return _Success(function(self._inner_value))

    def apply(self, container):
        """Calls a wrapped function in a container on this container."""
        if isinstance(container, self.success_type):
            return self.map(container.unwrap())  # type: ignore
        return container

    def bind(self, function):
        """Binds current container to a function that returns container."""
        return function(self._inner_value)

    #: Alias for `bind` method. Part of the `ResultBasedN` interface.
    bind_result = bind

    def lash(self, function):
        """Does nothing for ``Success``."""
        return self

    def alt(self, function):
        """Does nothing for ``Success``."""
        return self

    def value_or(self, default_value: _NewValueType) -> _ValueType:
        """Returns the value for successful container."""
        return self._inner_value

    def unwrap(self) -> _ValueType:
        """Returns the unwrapped value from successful container."""
        return self._inner_value

    def failure(self) -> NoReturn:
        """Raises an exception for successful container."""
        raise UnwrapFailedError(self)


Result.success_type = _Success
Result.failure_type = _Failure


# Public constructors:

def Success(  # noqa: N802
    inner_value: _NewValueType,
) -> Result[_NewValueType, Any]:
    """
    Public unit function of protected :class:`~_Success` type.

    .. code:: python

      >>> from returns.result import Success
      >>> assert str(Success(1)) == '<Success: 1>'

    """
    return _Success(inner_value)


def Failure(  # noqa: N802
    inner_value: _NewErrorType,
) -> Result[Any, _NewErrorType]:
    """
    Public unit function of protected :class:`~_Failure` type.

    .. code:: python

      >>> from returns.result import Failure
      >>> assert str(Failure(1)) == '<Failure: 1>'

    """
    return _Failure(inner_value)


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
ResultE = Result[_ValueType, Exception]


# Decorators:

def safe(
    function: Callable[..., _ValueType],
) -> Callable[..., ResultE[_ValueType]]:
    """
    Decorator to convert exception-throwing function to ``Result`` container.

    Should be used with care, since it only catches ``Exception`` subclasses.
    It does not catch ``BaseException`` subclasses.

    If you need to mark ``async`` function as ``safe``,
    use :func:`returns.future.future_safe` instead.
    This decorator only works with sync functions. Example:

    .. code:: python

      >>> from returns.result import Result, Success, safe

      >>> @safe
      ... def might_raise(arg: int) -> float:
      ...     return 1 / arg

      >>> assert might_raise(1) == Success(1.0)
      >>> assert isinstance(might_raise(0), Result.failure_type)

    Similar to :func:`returns.io.impure_safe`
    and :func:`returns.future.future_safe` decorators.

    Requires our :ref:`mypy plugin <mypy-plugins>`.

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            return Success(function(*args, **kwargs))
        except Exception as exc:
            return Failure(exc)
    return decorator
