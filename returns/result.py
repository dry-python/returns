# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Coroutine, TypeVar, Union, overload

from typing_extensions import final

from returns.primitives.container import (
    Container,
    FixableContainer,
    GenericContainerTwoSlots,
    ValueUnwrapContainer,
)
from returns.primitives.exceptions import UnwrapFailedError

# Regular type vars, work correctly:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_NewErrorType = TypeVar('_NewErrorType')


class Result(
    GenericContainerTwoSlots[_ValueType, _ErrorType],
    FixableContainer,
    ValueUnwrapContainer,
    metaclass=ABCMeta,
):
    """Base class for _Failure and _Success."""

    _inner_value: Union[_ValueType, _ErrorType]

    @abstractmethod  # noqa: A003
    def map(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':  # pragma: no cover
        """Abstract method to compose container with pure function."""
        raise NotImplementedError()

    @abstractmethod
    def bind(
        self,
        function: Callable[
            [_ValueType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, _NewErrorType]':  # pragma: no cover
        """Abstract method to compose container with other container."""
        raise NotImplementedError()

    @abstractmethod
    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':  # pragma: no cover
        """Abstract method to compose container with pure function."""
        raise NotImplementedError()

    @abstractmethod
    def rescue(
        self,
        function: Callable[
            [_ErrorType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, _NewErrorType]':  # pragma: no cover
        """Abstract method to compose container with other container."""
        raise NotImplementedError()

    @abstractmethod
    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:  # pragma: no cover
        """Get value or default value."""
        raise NotImplementedError()

    @abstractmethod
    def unwrap(self) -> _ValueType:  # pragma: no cover
        """Get value or raise exception."""
        raise NotImplementedError()

    @abstractmethod
    def failure(self) -> _ErrorType:  # pragma: no cover
        """Get failed value or raise exception."""
        raise NotImplementedError()


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
        Container.__init__(self, inner_value)  # type: ignore # noqa: Z462

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
        Container.__init__(self, inner_value)  # type: ignore # noqa: Z462

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

    def value_or(self, default_value):
        """Returns the value if we deal with '_Success' or default otherwise."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from the inside of this container."""
        return self._inner_value

    def failure(self):
        """Raises an exception, since it does not have an error inside."""
        raise UnwrapFailedError(self)


def Success(inner_value: _ValueType) -> Result[_ValueType, Any]:  # noqa: N802
    """Public unit function of protected `_Success` type."""
    return _Success(inner_value)


def Failure(inner_value: _ErrorType) -> Result[Any, _ErrorType]:  # noqa: N802
    """Public unit function of protected `_Failure` type."""
    return _Failure(inner_value)


@overload  # noqa: Z320
def safe(  # type: ignore
    function: Callable[..., Coroutine[_ValueType, _ErrorType, _NewValueType]],
) -> Callable[
    ...,
    Coroutine[_ValueType, _ErrorType, Result[_NewValueType, Exception]],
]:
    """Case for async functions."""


@overload
def safe(
    function: Callable[..., _NewValueType],
) -> Callable[..., Result[_NewValueType, Exception]]:
    """Case for regular functions."""


def safe(function):  # noqa: C901
    """
    Decorator to covert exception throwing function to 'Result' container.

    Should be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):
            try:
                return Success(await function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    else:
        def decorator(*args, **kwargs):
            try:
                return Success(function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    return wraps(function)(decorator)
