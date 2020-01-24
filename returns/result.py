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
          >>> Result.lift(example)(Success(2)) == Success(1.0)
          True

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

          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> Failure('a').map(mappable) == Failure('a')
          True

        """
        return self

    def bind(self, function):
        """
        Returns the '_Failure' instance that was used to call the method.

        .. code:: python

          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> Failure('a').bind(bindable) == Failure('a')
          True

        """
        return self

    def unify(self, function):
        """
        Returns the '_Failure' instance that was used to call the method.

        .. code:: python

          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> Failure('a').unify(bindable) == Failure('a')
          True

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

          >>> def fixable(arg: str) -> str:
          ...      return 'ab'
          ...
          >>> Failure('a').fix(fixable) == Success('ab')
          True

        """
        return _Success(function(self._inner_value))

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.

        .. code:: python

          >>> def rescuable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> Failure('a').rescue(rescuable) == Success('ab')
          True

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

          >>> def altable(arg: str) -> Result[str, str]:
          ...      return arg + 'b'
          ...
          >>> Failure('a').alt(altable) == Failure('ab')
          True

        """
        return _Failure(function(self._inner_value))

    def value_or(self, default_value):
        """
        Returns the value if we deal with '_Success' or default otherwise.

        .. code:: python

          >>> Failure(1).value_or(2)
          2

        """
        return default_value

    def unwrap(self):
        """
        Raises an exception, since it does not have a value inside.

        .. code:: python

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

          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> Success('a').map(mappable) == Success('ab')
          True

        """
        return _Success(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.

        .. code:: python

          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> Success('a').bind(bindable) == Success('ab')
          True

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

          >>> def bindable(string: str) -> Result[str, str]:
          ...      return Success(string + 'b')
          ...
          >>> Success('a').bind(bindable) == Success('ab')
          True

        """
        return self.bind(function)  # type: ignore

    def fix(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> def fixable(arg: str) -> str:
          ...      return 'ab'
          ...
          >>> Success('a').fix(fixable) == Success('a')
          True

        """
        return self

    def rescue(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> def rescuable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> Success('a').rescue(rescuable) == Success('a')
          True

        """
        return self

    def alt(self, function):
        """
        Returns the '_Success' instance that was used to call the method.

        .. code:: python

          >>> def altable(arg: str) -> Result[str, str]:
          ...      return Success(arg + 'b')
          ...
          >>> Success('a').alt(altable) == Success('a')
          True

        """
        return self

    def value_or(self, default_value):
        """
        Returns the value if we deal with '_Success' or default otherwise.

        .. code:: python

          >>> Success(1).value_or(2)
          1

        """
        return self._inner_value

    def unwrap(self):
        """
        Returns the unwrapped value from the inside of this container.

        .. code:: python

          >>> Success(1).unwrap()
          1

        """
        return self._inner_value

    def failure(self):
        """
        Raises an exception, since it does not have an error inside.

        .. code:: python

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
    inner_value: _ValueType,  # type: ignore
) -> Result[_ValueType, NoReturn]:
    """Public unit function of protected `_Success` type."""
    return _Success(inner_value)


def Failure(  # noqa: N802
    inner_value: _ErrorType,  # type: ignore
) -> Result[NoReturn, _ErrorType]:
    """Public unit function of protected `_Failure` type."""
    return _Failure(inner_value)


# Aliases:

ResultE = Result[_ValueType, Exception]


# Decorators:

@overload
def safe(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _ValueType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, Result[_ValueType, Exception]],
]:
    """Case for async functions."""


@overload
def safe(
    function: Callable[..., _ValueType],
) -> Callable[..., Result[_ValueType, Exception]]:
    """Case for regular functions."""


def safe(function):  # noqa: C901
    """
    Decorator to covert exception throwing function to 'Result' container.

    Should be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.

    Supports both async and regular functions.

    >>> @safe
    ... def might_raise(arg: int) -> float:
    ...     return 1 / arg
    ...
    >>> might_raise(1) == Success(1.0)
    True
    >>> isinstance(might_raise(0), _Failure)
    True

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
