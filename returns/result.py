# -*- coding: utf-8 -*-

from abc import ABCMeta
from functools import wraps
from inspect import iscoroutinefunction
from typing import (
    Any,
    Callable,
    Coroutine,
    Generic,
    NoReturn,
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
_DefaultValueType = TypeVar('_DefaultValueType')
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


class Result(
    Generic[_ValueType, _ErrorType],
    BaseContainer,
    metaclass=ABCMeta,
):
    """
    Base class for :class:`~_Failure` and :class:`~_Success`.

    :class:`~Result` does not have
    """

    _inner_value: Union[_ValueType, _ErrorType]

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
        default_value: _DefaultValueType,
    ) -> Union[_ValueType, _DefaultValueType]:
        """Get value or default value."""
        raise NotImplementedError

    def unwrap(self) -> _ValueType:
        """Get value or raise exception."""
        raise NotImplementedError

    def failure(self) -> _ErrorType:
        """Get failed value or raise exception."""
        raise NotImplementedError


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
        BaseContainer.__init__(self, inner_value)  # noqa: WPS609

    def map(self, function):  # noqa: A003
        """Returns the '_Failure' instance that was used to call the method."""
        return self

    def bind(self, function):
        """Returns the '_Failure' instance that was used to call the method."""
        return self

    def fix(self, function):
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the '_Success' instance
        and returns a new '_Success' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return _Success(function(self._inner_value))

    def rescue(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.
        """
        return function(self._inner_value)

    def alt(self, function):
        """
        Applies function to the error value.

        Applies 'function' to the contents of the '_Failure' instance
        and returns a new '_Failure' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return _Failure(function(self._inner_value))

    def value_or(self, default_value):
        """Returns the value if we deal with '_Success' or default otherwise."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        if isinstance(self._inner_value, Exception):
            raise UnwrapFailedError(self) from self._inner_value
        raise UnwrapFailedError(self)

    def failure(self):
        """Unwraps inner error value from failed container."""
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
        BaseContainer.__init__(self, inner_value)  # noqa: WPS609

    def map(self, function):  # noqa: A003
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the '_Success' instance
        and returns a new '_Success' object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.
        """
        return _Success(function(self._inner_value))

    def bind(self, function):
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return Result a '_Failure' or '_Success' type object.
        """
        return function(self._inner_value)

    def fix(self, function):
        """Returns the '_Success' instance that was used to call the method."""
        return self

    def rescue(self, function):
        """Returns the '_Success' instance that was used to call the method."""
        return self

    def alt(self, function):
        """Returns the '_Success' instance that was used to call the method."""
        return self

    def value_or(self, default_value):
        """Returns the value if we deal with '_Success' or default otherwise."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this container."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)


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
