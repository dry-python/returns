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
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


class Result(
    BaseContainer,
    Generic[_ValueType, _ErrorType],
    metaclass=ABCMeta,
):
    """
    Base class for :class:`~_Failure` and :class:`~_Success`.

    :class:`~Result` does not have a public contructor.
    Use :func:`~Success` and :func:`~Failure` to contruct the needed values.

    See also:
        https://bit.ly/361qQhi
        https://hackernoon.com/the-throw-keyword-was-a-mistake-l9e532di

    """

    _inner_value: Union[_ValueType, _ErrorType]

    # These two are required for projects like `classes`:
    success_type: ClassVar[Type['_Success']]
    failure_type: ClassVar[Type['_Failure']]

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """Abstract method to compose container with a pure function."""
        raise NotImplementedError

    def bind(
        self,
        function: Callable[[_ValueType], 'Result[_NewValueType, _ErrorType]'],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """Abstract method to compose a container with another container."""
        raise NotImplementedError

    def unify(
        self,
        function: Callable[
            [_ValueType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, Union[_ErrorType, _NewErrorType]]':
        """
        Abstract method to compose a container with another container.

        Similar to ``.bind``, but unifies the error type into a new type.
        It is useful when you have several functions to compose
        and each of them raises their own exceptions.
        That's a way to collect all of them.
        """
        raise NotImplementedError

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Abstract method to compose failed container and a pure function.

        This pure function should return a new state
        for a successful container.
        """
        raise NotImplementedError

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Abstract method to compose failed container and a pure function.

        This pure function should return a new state
        for a new failed container.
        """
        raise NotImplementedError

    def rescue(
        self,
        function: Callable[
            [_ErrorType], 'Result[_ValueType, _NewErrorType]',
        ],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Abstract method to compose a failed container with another container.

        This method is the oposite of ``.bind()``.
        """
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

    def failure(self) -> _ErrorType:
        """Get failed value or raise exception."""
        raise NotImplementedError

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[
        ['Result[_ValueType, _ErrorType]'],
        'Result[_NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``Result`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to: ``Result[a, error] -> Result[b, error]``

        Works similar to :meth:`~Result.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.result import Success, Result
          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not exactly IO action!
          ...
          >>> assert Result.lift(example)(Success(2)) == Success(1.0)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)


@final
class _Failure(Result[Any, _ErrorType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    Should not be used directly.
    """

    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        """Required for typing."""
        super().__init__(inner_value)

    def map(self, function):  # noqa: A003
        """
        Returns the '_Failure' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Failure
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Failure('a').map(mappable) == Failure('a')

        """
        return self

    def bind(self, function):
        """
        Returns the '_Failure' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Success, Failure
          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> assert Failure('a').bind(bindable) == Failure('a')

        """
        return self

    def unify(self, function):
        """
        Returns the '_Failure' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Success, Failure
          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> assert Failure('a').unify(bindable) == Failure('a')

        """
        return self

    def fix(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the '_Success' instance
        and returns a new '_Success' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> def fixable(arg: str) -> str:
          ...      return 'ab'
          ...
          >>> assert Failure('a').fix(fixable) == Success('ab')

        """
        return _Success(function(self._inner_value))

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.

        .. code:: python

          >>> from returns.result import Result, Success, Failure
          >>> def rescuable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> assert Failure('a').rescue(rescuable) == Success('ab')

        """
        return function(self._inner_value)

    def alt(self, function):
        """
        Applies function to the error value.

        Applies 'function' to the contents of the '_Failure' instance
        and returns a new '_Failure' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> from returns.result import Result, Failure
          >>> def altable(arg: str) -> Result[str, str]:
          ...      return arg + 'b'
          ...
          >>> assert Failure('a').alt(altable) == Failure('ab')

        """
        return _Failure(function(self._inner_value))

    def value_or(self, default_value):
        """
        Returns the value if we deal with '_Success' or default otherwise.

        .. code:: python

          >>> from returns.result import Failure
          >>> Failure(1).value_or(2)
          2

        """
        return default_value

    def unwrap(self):
        """
        Raises an exception, since it does not have a value inside.

        .. code:: python

          >>> from returns.result import Failure
          >>> Failure(1).unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        if isinstance(self._inner_value, Exception):
            raise UnwrapFailedError(self) from self._inner_value
        raise UnwrapFailedError(self)

    def failure(self):
        """
        Unwraps inner error value from failed container.

        .. code:: python

          >>> from returns.result import Failure
          >>> Failure(1).failure()
          1

        """
        return self._inner_value


@final
class _Success(Result[_ValueType, Any]):
    """
    Represents a calculation which has succeeded and contains the result.

    Contains the computation value.
    Should not be used directly.
    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Required for typing."""
        super().__init__(inner_value)

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the '_Success' instance
        and returns a new '_Success' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> from returns.result import Success
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Success('a').map(mappable) == Success('ab')

        """
        return _Success(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> assert Success('a').bind(bindable) == Success('ab')

        """
        return function(self._inner_value)

    def unify(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        It is the same as ``.bind``, but handles type signatures differently.
        While ``.bind`` forces to respect error type and not changing it,
        ``.unify`` allows to return a ``Union`` of previous
        error types and new ones.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> assert Success('a').bind(bindable) == Success('ab')

        """
        return self.bind(function)  # type: ignore

    def fix(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Success
          >>> def fixable(arg: str) -> str:
          ...      return 'ab'
          ...
          >>> assert Success('a').fix(fixable) == Success('a')

        """
        return self

    def rescue(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> def rescuable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> assert Success('a').rescue(rescuable) == Success('a')

        """
        return self

    def alt(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> def altable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> assert Success('a').alt(altable) == Success('a')

        """
        return self

    def value_or(self, default_value):
        """
        Returns the value if we deal with '_Success' or default otherwise.

        .. code:: python

          >>> from returns.result import Success
          >>> Success(1).value_or(2)
          1

        """
        return self._inner_value

    def unwrap(self):
        """
        Returns the unwrapped value from the inside of this container.

        .. code:: python

          >>> from returns.result import Success
          >>> Success(1).unwrap()
          1

        """
        return self._inner_value

    def failure(self):
        """
        Raises an exception, since it does not have an error inside.

        .. code:: python

          >>> from returns.result import Success
          >>> Success(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise UnwrapFailedError(self)


Result.success_type = _Success
Result.failure_type = _Failure


# Public constructors:

def Success(  # noqa: N802
    inner_value: _NewValueType,
) -> Result[_NewValueType, NoReturn]:
    """
    Public unit function of protected :class:`~_Success` type.

    .. code:: python

      >>> from returns.result import Success
      >>> str(Success(1))
      '<Success: 1>'

    """
    return _Success(inner_value)


def Failure(  # noqa: N802
    inner_value: _NewErrorType,
) -> Result[NoReturn, _NewErrorType]:
    """
    Public unit function of protected :class:`~_Failure` type.

    .. code:: python

      >>> from returns.result import Failure
      >>> str(Failure(1))
      '<Failure: 1>'

    """
    return _Failure(inner_value)


# Aliases:

#: A popular case for writing `Result` is using `Exception` as the last type.
ResultE = Result[_ValueType, Exception]


# Decorators:

@overload
def safe(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _ValueType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, ResultE[_ValueType]],
]:
    """Case for async functions."""


@overload
def safe(
    function: Callable[..., _ValueType],
) -> Callable[..., ResultE[_ValueType]]:
    """Case for regular functions."""


def safe(function):  # noqa: C901
    """
    Decorator to covert exception throwing function to 'Result' container.

    Should be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.

    Supports both async and regular functions.

    >>> from returns.result import Result, Success, safe
    >>> @safe
    ... def might_raise(arg: int) -> float:
    ...     return 1 / arg
    ...
    >>> assert might_raise(1) == Success(1.0)
    >>> assert isinstance(might_raise(0), Result.failure_type)

    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):  # noqa: WPS430
            try:
                return Success(await function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    else:
        def decorator(*args, **kwargs):  # noqa: WPS430
            try:
                return Success(function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    return wraps(function)(decorator)
