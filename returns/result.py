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
_ContraErrorType = TypeVar('_ContraErrorType', contravariant=True)

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
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> def mappable(string: str) -> str:
          ...      return string + 'b'
          ...
          >>> assert Success('a').map(mappable) == Success('ab')
          >>> assert Failure('a').map(mappable) == Failure('a')

        """
        raise NotImplementedError

    def bind(
        self,
        function: Callable[[_ValueType], 'Result[_NewValueType, _ErrorType]'],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.result import Result, Success, Failure
          >>> def bindable(arg: str) -> Result[str, str]:
          ...      if len(arg) > 1:
          ...          return Success(arg + 'b')
          ...      return Failure(arg + 'c')
          ...
          >>> assert Success('aa').bind(bindable) == Success('aab')
          >>> assert Success('a').bind(bindable) == Failure('ac')
          >>> assert Failure('a').bind(bindable) == Failure('a')

        """
        raise NotImplementedError

    def unify(
        self,
        function: Callable[
            [_ValueType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, Union[_ErrorType, _NewErrorType]]':
        """
        Composes successful container with a function that returns a container.

        Similar to :meth:`~Result.bind` but has different type.
        It returns ``Result[ValueType, Union[OldErrorType, NewErrorType]]``
        instead of ``Result[ValueType, OldErrorType]``.

        So, it can be more useful in some situations.
        Probably with specific exceptions.

        .. code:: python

          >>> from returns.result import Result, Success, Failure
          >>> def bindable(arg: str) -> Result[str, str]:
          ...      if len(arg) > 1:
          ...          return Success(arg + 'b')
          ...      return Failure(arg + 'c')
          ...
          >>> assert Success('aa').unify(bindable) == Success('aab')
          >>> assert Success('a').unify(bindable) == Failure('ac')
          >>> assert Failure('a').unify(bindable) == Failure('a')

        """
        raise NotImplementedError

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function to fix the failure.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> def fixable(arg: str) -> str:
          ...      return 'ab'
          ...
          >>> assert Success('a').fix(fixable) == Success('a')
          >>> assert Failure('a').fix(fixable) == Success('ab')

        """
        raise NotImplementedError

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function to modify failure.

        .. code:: python

          >>> from returns.result import Result, Failure, Success
          >>> def altable(arg: str) -> Result[str, str]:
          ...      return arg + 'b'
          ...
          >>> assert Success('a').alt(altable) == Success('a')
          >>> assert Failure('a').alt(altable) == Failure('ab')

        """
        raise NotImplementedError

    def rescue(
        self,
        function: Callable[
            [_ErrorType], 'Result[_ValueType, _NewErrorType]',
        ],
    ) -> 'Result[_ValueType, _NewErrorType]':
        """
        Composes failed container with a function that returns a container.

        .. code:: python

          >>> from returns.result import Result, Success, Failure
          >>> def rescuable(arg: str) -> Result[str, str]:
          ...      if len(arg) > 1:
          ...          return Success(arg + 'b')
          ...      return Failure(arg + 'c')
          ...
          >>> assert Success('a').rescue(rescuable) == Success('a')
          >>> assert Failure('a').rescue(rescuable) == Failure('ac')
          >>> assert Failure('aa').rescue(rescuable) == Success('aab')

        """
        raise NotImplementedError

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
        raise NotImplementedError

    def unwrap(self) -> _ValueType:
        """
        Get value or raise exception.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> assert Success(1).unwrap() == 1

        .. code::

          >>> Failure(1).unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise NotImplementedError

    def failure(self) -> _ErrorType:
        """
        Get failed value or raise exception.

        .. code:: python

          >>> from returns.result import Failure, Success
          >>> assert Failure(1).failure() == 1

        .. code::

          >>> Success(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        raise NotImplementedError

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[
        ['Result[_ValueType, _ContraErrorType]'],
        'Result[_NewValueType, _ContraErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``Result`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to: ``Result[a, error] -> Result[b, error]``

        Works similar to :meth:`~Result.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> from returns.result import Success, Result, Failure
          >>> def example(argument: int) -> float:
          ...     return argument / 2
          ...
          >>> assert Result.lift(example)(Success(2)) == Success(1.0)
          >>> assert Result.lift(example)(Failure(2)) == Failure(2)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def from_success(
        cls, inner_value: _NewValueType,
    ) -> 'Result[_NewValueType, Any]':
        """
        One more value to create success unit values.

        This is a part of :class:`returns.primitives.interfaces.Unitable`.
        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.result import Result, Success
          >>> assert Result.from_success(1) == Success(1)

        You can use this method or :func:`~Success`,
        choose the most convenient for you.

        """
        return Success(inner_value)

    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType,
    ) -> 'Result[Any, _NewErrorType]':
        """
        One more value to create failred unit values.

        This is a part of :class:`returns.primitives.interfaces.Unitable`.
        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.result import Result, Failure
          >>> assert Result.from_failure(1) == Failure(1)

        You can use this method or :func:`~Failure`,
        choose the most convenient for you.

        """
        return Failure(inner_value)


@final
class _Failure(Result[Any, _ErrorType]):
    """
    Represents a calculation which has failed.

    It should contain an error code or message.
    Should not be used directly.

    This is an implementation detail, please, do not use it directly.
    This class only has method that are logically
    dependent on the current container state: successful or failed.

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

    def map(self, function):  # noqa: A003
        """Does nothing for ``Failure``."""
        return self

    def bind(self, function):
        """Does nothing for ``Failure``."""
        return self

    def unify(self, function):
        """Does nothing for ``Failure``."""
        return self

    def fix(self, function):
        """Composes pure function with a failed container."""
        return _Success(function(self._inner_value))

    def rescue(self, function):
        """Composes this container with a function returning container."""
        return function(self._inner_value)

    def alt(self, function):
        """Composes failed container with a pure function to modify failure."""
        return _Failure(function(self._inner_value))

    def value_or(self, default_value):
        """Returns default value for failed container."""
        return default_value

    def unwrap(self):
        """Raises an exception, since it does not have a value inside."""
        if isinstance(self._inner_value, Exception):
            raise UnwrapFailedError(self) from self._inner_value
        raise UnwrapFailedError(self)

    def failure(self):
        """Returns failed value."""
        return self._inner_value


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

    def map(self, function):  # noqa: A003
        """Composes current container with a pure function."""
        return _Success(function(self._inner_value))

    def bind(self, function):
        """Binds current container to a function that returns container."""
        return function(self._inner_value)

    def unify(self, function):
        """
        Binds current container to a function that returns container.

        Similar as :meth:`~_Success.bind`
        but modifies the return type to unify error types.
        """
        return self.bind(function)  # type: ignore

    def fix(self, function):
        """Does nothing for ``Success``."""
        return self

    def rescue(self, function):
        """Does nothing for ``Success``."""
        return self

    def alt(self, function):
        """Does nothing for ``Success``."""
        return self

    def value_or(self, default_value):
        """Returns the value for successful container."""
        return self._inner_value

    def unwrap(self):
        """Returns the unwrapped value from successful container."""
        return self._inner_value

    def failure(self):
        """Raises an exception for succesful container."""
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
      >>> str(Success(1))
      '<Success: 1>'

    """
    return _Success(inner_value)


def Failure(  # noqa: N802
    inner_value: _NewErrorType,
) -> Result[Any, _NewErrorType]:
    """
    Public unit function of protected :class:`~_Failure` type.

    .. code:: python

      >>> from returns.result import Failure
      >>> str(Failure(1))
      '<Failure: 1>'

    """
    return _Failure(inner_value)


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
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
