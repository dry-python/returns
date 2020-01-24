# -*- coding: utf-8 -*-

from abc import ABCMeta
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Generic, TypeVar, overload, Union, NoReturn

from typing_extensions import final

from returns._generated.squash import _squash as io_squash  # noqa: F401, WPS436
from returns.primitives.container import BaseContainer
from returns.result import Result, Success, Failure
from returns.pipeline import is_successful

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Result related:
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(BaseContainer, Generic[_ValueType]):
    """
    Explicit marker for impure function results.

    We call it "marker" since once it is marked, it cannot be unmarked.

    ``IO`` is also a container.
    But, it is different in a way that it can't be unwrapped / rescued / fixed.
    There's no way to directly get its internal value.

    Note that IO represents a computation that never fails.

    Examples of such computations are:

    - read / write to localStorage
    - get the current time
    - write to the console
    - get a random number

    Use ``IOResult[...]`` for operations that might fail.
    Like DB access or network operations.

    See also:
        https://dev.to/gcanti/getting-started-with-fp-ts-io-36p6

    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Required for typing."""
        super().__init__(inner_value)

    def map(  # noqa: A003
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
          ...
          >>> IO('a').map(mappable) == IO('ab')
          True

        """
        return IO(function(self._inner_value))

    def bind(
        self, function: Callable[[_ValueType], 'IO[_NewValueType]'],
    ) -> 'IO[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return IO type object.

        .. code:: python

          >>> def bindable(string: str) -> IO[str]:
          ...      return IO(string + 'b')
          ...
          >>> IO('a').bind(bindable) == IO('ab')
          True

        """
        return function(self._inner_value)

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[['IO[_ValueType]'], 'IO[_NewValueType]']:
        """
        Lifts function to be wrapped in ``IO`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to: ``IO[a] -> IO[b]``

        Works similar to :meth:`~IO.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not exactly IO action!
          ...
          >>> IO.lift(example)(IO(2)) == IO(1.0)
          True

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)


@final
class IOResult(BaseContainer, Generic[_ValueType, _ErrorType]):

    _inner_value: Result[_ValueType, _ErrorType]

    def __init__(self, inner_value: Result[_ValueType, _ErrorType]) -> None:
        """Required for typing."""
        super().__init__(inner_value)

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'IOResult[_NewValueType, _ErrorType]',
        ],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        if is_successful(self._inner_value):
            return function(self._inner_value.unwrap())
        return self  # type: ignore

    def map(
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        return IOResult(self._inner_value.map(function))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'IOResult[_ValueType, _NewErrorType]',
        ],
    ) -> 'IOResult[_ValueType, _NewErrorType]':
        if is_successful(self._inner_value):
            return self  # type: ignore
        return function(self._inner_value.failure())

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        return IOResult(self._inner_value.fix(function))

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'IOResult[_ValueType, _NewErrorType]':
        return IOResult(self._inner_value.alt(function))

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> IO[Union[_ValueType, _NewValueType]]:
        """Get value or default value."""
        return IO(self._inner_value.value_or(default_value))

    def unwrap(self) -> IO[_ValueType]:
        """Get value or raise exception."""
        return IO(self._inner_value.unwrap())

    def failure(self) -> IO[_ErrorType]:
        """Get failed value or raise exception."""
        return IO(self._inner_value.failure())

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[
        ['IOResult[_ValueType, _ErrorType]'],
        'IOResult[_NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``IOResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to:
        ``IOResult[a, error] -> IOResult[b, error]``

        Works similar to :meth:`~IOResult.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.io import IOResult, IOSuccess
          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not exactly IO action!
          ...
          >>> IOResult.lift(example)(IOSuccess(2)) == IOSuccess(1.0)
          True

        This one is similar to appling :meth:`~IO.lift`
        and :meth:`returns.result.Result.lift` in order.

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def from_typecast(
        cls, container: IO[Result[_ValueType, _ErrorType]],
    ) -> IOResult[_ValueType, _ErrorType]:
        return cls(container._inner_value)


def IOSuccess(inner_value: _NewValueType) -> IOResult[_NewValueType, NoReturn]:
    return IOResult(Success(inner_value))


def IOFailure(inner_value: _NewErrorType) -> IOResult[NoReturn, _NewErrorType]:
    return IOResult(Failure(inner_value))

# TODO: @impure with `IOResult`?


@overload
def impure(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _NewValueType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, IO[_NewValueType]],
]:
    """Case for async functions."""


@overload
def impure(
    function: Callable[..., _NewValueType],
) -> Callable[..., IO[_NewValueType]]:
    """Case for regular functions."""


def impure(function):
    """
    Decorator to mark function that it returns :py:class:`IO` container.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):  # noqa: WPS430
            return IO(await function(*args, **kwargs))
    else:
        def decorator(*args, **kwargs):  # noqa: WPS430
            return IO(function(*args, **kwargs))
    return wraps(function)(decorator)
