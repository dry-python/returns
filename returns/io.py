from abc import ABCMeta
from functools import wraps
from typing import Any, Callable, ClassVar, Generic, Type, TypeVar, Union

from typing_extensions import final

from returns.primitives.container import BaseContainer
from returns.result import Failure, Result, Success

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')

# Result related:
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')
_ContraErrorType = TypeVar('_ContraErrorType', contravariant=True)

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(BaseContainer, Generic[_ValueType]):
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
        https://dev.to/gcanti/getting-started-with-fp-ts-io-36p6
        https://gist.github.com/chris-taylor/4745921

    """

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """
        Public constructor for this type. Also required for typing.

        .. code:: python

          >>> from returns.io import IO
          >>> str(IO(1))
          '<IO: 1>'

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
        container: 'IO[Callable[[_ValueType], _NewValueType]]',
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
        return self.map(container._inner_value)  # noqa: WPS437

    def bind(
        self, function: Callable[[_ValueType], 'IO[_NewValueType]'],
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
        return function(self._inner_value)

    @classmethod
    def from_value(cls, inner_value: _NewValueType) -> 'IO[_NewValueType]':
        """
        Unit function to construct new ``IO`` values.

        Is the same as regular constructor:

        .. code:: python

          >>> from returns.io import IO
          >>> assert IO(1) == IO.from_value(1)

        Part of the :class:`returns.primitives.interfaces.Applicative`
        protocol.
        """
        return IO(inner_value)

    @classmethod
    def from_ioresult(
        cls,
        container: 'IOResult[_NewValueType, _ErrorType]',
    ) -> 'IO[Result[_NewValueType, _ErrorType]]':
        """
        Converts ``IOResult[a, b]`` back to ``IO[Result[a, b]]``.

        Can be really helpful for composition.

        .. code:: python

            >>> from returns.io import IO, IOSuccess
            >>> from returns.result import Success
            >>> assert IO.from_ioresult(IOSuccess(1)) == IO(Success(1))

        Is the reverse of :meth:`returns.io.IOResult.from_typecast`.
        """
        return IO(container._inner_value)  # noqa: WPS437


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


# IO and Result:

class IOResult(
    BaseContainer,
    Generic[_ValueType, _ErrorType],
    metaclass=ABCMeta,
):
    """
    Explicit container for impure function results that might fail.

    Definition
    ~~~~~~~~~~

    This type is similar to :class:`returns.result.Result`.
    This basically a more useful version of ``IO[Result[a, b]]``.
    Use this type for ``IO`` computations that might fail.
    Examples of ``IO`` computations that might fail are:

    - access database
    - access network
    - access filesystem

    Use :class:`~IO` for operations that do ``IO`` but do not fail.

    Note, that even methods like :meth:`~IOResult.unwrap``
    and :meth:`~IOResult.value_or` return values wrapped in ``IO``.

    ``IOResult`` is a complex compound value that consists of:

    - raw value
    - ``Result``
    - ``IO``

    This is why it has so many helper and factory methods:

    - You can construct ``IOResult`` from raw values
      with :func:`~IOSuccess` and :func:`~IOFailure` public type constructors
    - You can construct ``IOResult`` from ``IO`` values
      with :meth:`~IOResult.from_failed_io`
      and :meth:`IOResult.from_io`
    - You can construct ``IOResult`` from ``Result`` values
      with :meth:`~IOResult.from_result`

    We also have a lot of utility methods for better function composition like:

    - :meth:`~IOResult.bind_result` to work
      with functions which return ``Result``
    - :meth:`~IOResult.from_typecast` to work with ``IO[Result[...]]`` values

    See also:
        https://github.com/gcanti/fp-ts/blob/master/docs/modules/IOEither.ts.md


    Implementation
    ~~~~~~~~~~~~~~

    This class contains all the methods that can be delegated to ``Result``.
    But, some methods have ``raise NotImplementedError`` which means
    that we have to use special :class:`~_IOSuccess` and :class:`~_IOFailure`
    implementation details to correctly handle these callbacks.

    Do not rely on them! Use public data.

    """

    _inner_value: Result[_ValueType, _ErrorType]

    # These two are required for projects like `classes`:
    #: Success type that is used to represent the successful computation.
    success_type: ClassVar[Type['_IOSuccess']]
    #: Failure type that is used to represent the failed computation.
    failure_type: ClassVar[Type['_IOFailure']]

    def __init__(self, inner_value: Result[_ValueType, _ErrorType]) -> None:
        """
        Private type constructor.

        Use :func:`~IOSuccess` and :func:`~IOFailure` instead.
        Or :meth:`~IOResult.from_result` factory.
        """
        super().__init__(inner_value)

    def map(  # noqa: WPS125
        self, function: Callable[[_ValueType], _NewValueType],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Composes successful container with a pure function.

        .. code:: python

          >>> from returns.io import IOSuccess
          >>> assert IOSuccess(1).map(lambda num: num + 1) == IOSuccess(2)

        """
        return self.from_result(self._inner_value.map(function))

    def apply(
        self,
        container:
            'IOResult[Callable[[_ValueType], _NewValueType], _ErrorType]',
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Calls a wrapped function in a container on this container.

        .. code:: python

          >>> from returns.io import IOSuccess, IOFailure, IOResult

          >>> def appliable(first: str) -> str:
          ...      return first + 'b'

          >>> assert IOSuccess('a').apply(
          ...     IOSuccess(appliable),
          ... ) == IOSuccess('ab')
          >>> assert IOFailure('a').apply(
          ...     IOSuccess(appliable),
          ... ) == IOFailure('a')

          >>> assert isinstance(IOSuccess('a').apply(
          ...     IOFailure(appliable),
          ... ), IOResult.failure_type)

        """
        if isinstance(container, self.success_type):
            return self.from_result(
                self._inner_value.map(
                    container.unwrap()._inner_value,  # noqa: WPS437
                ),
            )
        return container  # type: ignore

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'IOResult[_NewValueType, _ErrorType]',
        ],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.io import IOResult, IOFailure, IOSuccess
          >>> def bindable(string: str) -> IOResult[str, str]:
          ...      if len(string) > 1:
          ...          return IOSuccess(string + 'b')
          ...      return IOFailure(string + 'c')

          >>> assert IOSuccess('aa').bind(bindable) == IOSuccess('aab')
          >>> assert IOSuccess('a').bind(bindable) == IOFailure('ac')
          >>> assert IOFailure('a').bind(bindable) == IOFailure('a')

        """
        raise NotImplementedError

    def bind_result(
        self,
        function: Callable[
            [_ValueType],
            'Result[_NewValueType, _ErrorType]',
        ],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Composes successful container with a function that returns a container.

        Similar to :meth:`~IOResult.bind`, but works with containers
        that return :class:`returns.result.Result`
        instead of :class:`~IOResult`.

        .. code:: python

          >>> from returns.io import IOFailure, IOSuccess
          >>> from returns.result import Result, Success

          >>> def bindable(string: str) -> Result[str, str]:
          ...      if len(string) > 1:
          ...          return Success(string + 'b')
          ...      return Failure(string + 'c')

          >>> assert IOSuccess('aa').bind_result(bindable) == IOSuccess('aab')
          >>> assert IOSuccess('a').bind_result(bindable) == IOFailure('ac')
          >>> assert IOFailure('a').bind_result(bindable) == IOFailure('a')

        """
        raise NotImplementedError

    def bind_io(
        self,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Composes successful container with a function that returns a container.

        Similar to :meth:`~IOResult.bind`, but works with containers
        that return :class:`returns.io.IO` instead of :class:`~IOResult`.

        .. code:: python

          >>> from returns.io import IO, IOFailure, IOSuccess

          >>> def bindable(string: str) -> IO[str]:
          ...      return IO(string + 'z')

          >>> assert IOSuccess('a').bind_io(bindable) == IOSuccess('az')
          >>> assert IOFailure('a').bind_io(bindable) == IOFailure('a')

        """
        raise NotImplementedError

    def unify(
        self,
        function: Callable[
            [_ValueType],
            'IOResult[_NewValueType, _NewErrorType]',
        ],
    ) -> 'IOResult[_NewValueType, Union[_ErrorType, _NewErrorType]]':
        """
        Composes successful container with a function that returns a container.

        .. code:: python

          >>> from returns.io import IOResult, IOFailure, IOSuccess
          >>> def bindable(string: str) -> IOResult[str, str]:
          ...      if len(string) > 1:
          ...          return IOSuccess(string + 'b')
          ...      return IOFailure(string + 'c')

          >>> assert IOSuccess('aa').unify(bindable) == IOSuccess('aab')
          >>> assert IOSuccess('a').unify(bindable) == IOFailure('ac')
          >>> assert IOFailure('a').unify(bindable) == IOFailure('a')

        """
        return self.bind(function)  # type: ignore

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'IOResult[_NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function to fix the failure.

        .. code:: python

          >>> from returns.io import IOFailure, IOSuccess
          >>> assert IOFailure('a').fix(
          ...     lambda char: char + 'b',
          ... ) == IOSuccess('ab')

        """
        return self.from_result(self._inner_value.fix(function))

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'IOResult[_ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function to modify failure.

        .. code:: python

          >>> from returns.io import IOFailure
          >>> assert IOFailure(1).alt(float) == IOFailure(1.0)

        """
        return self.from_result(self._inner_value.alt(function))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'IOResult[_ValueType, _NewErrorType]',
        ],
    ) -> 'IOResult[_ValueType, _NewErrorType]':
        """
        Composes failed container with a function that returns a container.

        .. code:: python

          >>> from returns.io import IOFailure, IOSuccess, IOResult
          >>> def rescuable(state: str) -> IOResult[int, str]:
          ...     if len(state) > 1:
          ...         return IOSuccess(len(state))
          ...     return IOFailure('oops')

          >>> assert IOFailure('a').rescue(rescuable) == IOFailure('oops')
          >>> assert IOFailure('abc').rescue(rescuable) == IOSuccess(3)
          >>> assert IOSuccess('a').rescue(rescuable) == IOSuccess('a')

        """
        raise NotImplementedError

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> IO[Union[_ValueType, _NewValueType]]:
        """
        Get value from successful container or default value from failed one.

        .. code:: python

          >>> from returns.io import IO, IOFailure, IOSuccess
          >>> assert IOSuccess(1).value_or(None) == IO(1)
          >>> assert IOFailure(1).value_or(None) == IO(None)

        """
        return IO(self._inner_value.value_or(default_value))

    def unwrap(self) -> IO[_ValueType]:
        """
        Get value from successful container or raise exception for failed one.

        .. code:: python

          >>> from returns.io import IO, IOFailure, IOSuccess
          >>> assert IOSuccess(1).unwrap() == IO(1)

        .. code::

          >>> IOFailure(1).unwrap()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return IO(self._inner_value.unwrap())

    def failure(self) -> IO[_ErrorType]:
        """
        Get failed value from failed container or raise exception from success.

        .. code:: python

          >>> from returns.io import IO, IOFailure, IOSuccess
          >>> assert IOFailure(1).failure() == IO(1)

        .. code::

          >>> IOSuccess(1).failure()
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return IO(self._inner_value.failure())

    @classmethod
    def from_typecast(
        cls, container: IO[Result[_NewValueType, _NewErrorType]],
    ) -> 'IOResult[_NewValueType, _NewErrorType]':
        """
        Converts ``IO[Result[_ValueType, _ErrorType]]`` to ``IOResult``.

        Also prevails the type of ``Result`` to ``IOResult``, so:
        ``IO[Result[_ValueType, _ErrorType]]`` would become
        ``IOResult[_ValueType, _ErrorType]``.

        .. code:: python

          >>> from returns.result import Success
          >>> from returns.io import IO, IOResult, IOSuccess
          >>> container = IO(Success(1))
          >>> assert IOResult.from_typecast(container) == IOSuccess(1)

        Can be reverted via :meth:`returns.io.IO.from_ioresult` method.
        """
        return cls.from_result(container._inner_value)  # noqa: WPS437

    @classmethod
    def from_failed_io(
        cls, container: IO[_NewErrorType],
    ) -> 'IOResult[Any, _NewErrorType]':
        """
        Creates new ``IOResult`` from "failed" ``IO`` container.

        .. code:: python

          >>> from returns.io import IO, IOResult, IOFailure
          >>> container = IO(1)
          >>> assert IOResult.from_failed_io(container) == IOFailure(1)

        """
        return IOFailure(container._inner_value)  # noqa: WPS437

    @classmethod
    def from_io(
        cls, container: IO[_NewValueType],
    ) -> 'IOResult[_NewValueType, Any]':
        """
        Creates new ``IOResult`` from "successful" ``IO`` container.

        .. code:: python

          >>> from returns.io import IO, IOResult, IOSuccess
          >>> container = IO(1)
          >>> assert IOResult.from_io(container) == IOSuccess(1)

        """
        return IOSuccess(container._inner_value)  # noqa: WPS437

    @classmethod
    def from_result(
        cls, container: Result[_NewValueType, _NewErrorType],
    ) -> 'IOResult[_NewValueType, _NewErrorType]':
        """
        Creates ``IOResult`` from ``Result`` value.

        .. code:: python

          >>> from returns.io import IOResult, IOSuccess, IOFailure
          >>> from returns.result import Success, Failure

          >>> assert IOResult.from_result(Success(1)) == IOSuccess(1)
          >>> assert IOResult.from_result(Failure(2)) == IOFailure(2)

        """
        if isinstance(container, container.success_type):
            return _IOSuccess(container)
        return _IOFailure(container)

    @classmethod
    def from_value(
        cls, inner_value: _NewValueType,
    ) -> 'IOResult[_NewValueType, Any]':
        """
        One more value to create success unit values.

        This is a part of :class:`returns.primitives.interfaces.Unitable`.
        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.io import IOResult, IOSuccess
          >>> assert IOResult.from_value(1) == IOSuccess(1)

        You can use this method or :func:`~IOSuccess`,
        choose the most convenient for you.

        """
        return IOSuccess(inner_value)

    @classmethod
    def from_failure(
        cls, inner_value: _NewErrorType,
    ) -> 'IOResult[Any, _NewErrorType]':
        """
        One more value to create failure unit values.

        This is a part of :class:`returns.primitives.interfaces.Unitable`.
        It is useful as a united way to create a new value from any container.

        .. code:: python

          >>> from returns.io import IOResult, IOFailure
          >>> assert IOResult.from_failure(1) == IOFailure(1)

        You can use this method or :func:`~IOFailure`,
        choose the most convenient for you.

        """
        return IOFailure(inner_value)

    def __str__(self) -> str:
        """Custom ``str`` representation for better readability."""
        return '<IOResult: {0}>'.format(self._inner_value)


@final
class _IOFailure(IOResult):
    """
    Internal ``IOFailure`` representation.

    This is an implementation detail, please, do not use it directly.
    This class only has method that are logically
    dependent on the current container state: successful or failed.

    Use public data types instead!
    """

    def __init__(self, inner_value) -> None:
        """
        Private type constructor.

        Use :func:`~IOSuccess` and :func:`~IOFailure` instead.
        Or :meth:`~IOResult.from_result` factory.
        """
        super().__init__(inner_value)

    def bind(self, function):
        """Does nothing for ``IOFailure``."""
        return self

    def bind_result(self, function):
        """Does nothing for ``IOFailure``."""
        return self

    def bind_io(self, function):
        """Does nothing for ``IOFailure``."""
        return self

    def rescue(self, function):
        """Composes this container with a function returning ``IOResult``."""
        return function(self._inner_value.failure())


@final
class _IOSuccess(IOResult):
    """
    Internal ``IOSuccess`` representation.

    This is an implementation detail, please, do not use it directly.
    This class only has method that are logically
    dependent on the current container state: successful or failed.

    Use public data types instead!
    """

    def __init__(self, inner_value) -> None:
        """
        Private type constructor.

        Use :func:`~IOSuccess` and :func:`~IOFailure` instead.
        Or :meth:`~IOResult.from_result` factory.
        """
        super().__init__(inner_value)

    def bind(self, function):
        """Composes this container with a function returning ``IOResult``."""
        return function(self._inner_value.unwrap())

    def bind_result(self, function):
        """Binds ``Result`` returning function to current container."""
        return self.from_result(function(self._inner_value.unwrap()))

    def bind_io(self, function):
        """Binds ``IO`` returning function to current container."""
        return self.from_io(function(self._inner_value.unwrap()))

    def rescue(self, function):
        """Does nothing for ``IOSuccess``."""
        return self


# Public type constructors:

def IOSuccess(  # noqa: N802
    inner_value: _NewValueType,
) -> IOResult[_NewValueType, Any]:
    """
    Public unit function of successful :class:`~IOResult` container.

    .. code:: python

      >>> from returns.io import IOSuccess
      >>> str(IOSuccess(1))
      '<IOResult: <Success: 1>>'

    """
    return _IOSuccess(Success(inner_value))


def IOFailure(  # noqa: N802
    inner_value: _NewErrorType,
) -> IOResult[Any, _NewErrorType]:
    """
    Public unit function of failed :class:`~IOResult` container.

    .. code:: python

      >>> from returns.io import IOFailure
      >>> str(IOFailure(1))
      '<IOResult: <Failure: 1>>'

    """
    return _IOFailure(Failure(inner_value))


IOResult.success_type = _IOSuccess
IOResult.failure_type = _IOFailure


# Aliases:

#: Alias for a popular case when ``IOResult`` has ``Exception`` as error type.
IOResultE = IOResult[_ValueType, Exception]


# impure_safe decorator:

def impure_safe(
    function: Callable[..., _NewValueType],
) -> Callable[..., IOResultE[_NewValueType]]:
    """
    Decorator to mark function that it returns :class:`~IOResult` container.

    Should be used with care, since it only catches ``Exception`` subclasses.
    It does not catch ``BaseException`` subclasses.

    If you need to mark ``async`` function as impure,
    use :func:`returns.future.future_safe` instead.
    This decorator only works with sync functions. Example:

    .. code:: python

      >>> from returns.io import IOSuccess, impure_safe

      >>> @impure_safe
      ... def function(arg: int) -> float:
      ...     return 1 / arg
      ...

      >>> assert function(1) == IOSuccess(1.0)
      >>> assert function(0).failure()

    Similar to :func:`returns.future.future_safe`
    and :func:`returns.result.safe` decorators.

    Requires our :ref:`mypy plugin <mypy-plugins>`.

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            return IOSuccess(function(*args, **kwargs))
        except Exception as exc:
            return IOFailure(exc)
    return decorator
