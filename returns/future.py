from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Generic,
    TypeVar,
    Union,
)

from typing_extensions import final

from returns._generated.futures import _future, _future_result
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer
from returns.result import Failure, Result, Success

# Definitions:
_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')
_ContraErrorType = TypeVar('_ContraErrorType', contravariant=True)

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


# Public composition helpers:

async def async_identity(instance: _FirstType) -> _FirstType:
    """
    Async function that returns its argument.

    .. code:: python

      >>> import anyio
      >>> from returns.future import async_identity
      >>> assert anyio.run(async_identity, 1) == 1

    See :func:`returns.functions.identity`
    for sync version of this function and more docs and examples.

    """
    return instance


# Future
# ======

@final
class Future(BaseContainer, Generic[_ValueType]):
    """
    Container to easily compose ``async`` functions.

    Represents a better abstraction over a simple coroutine.

    Is framework, event-loop, and IO-library agnostics.
    Works with ``asyncio``, ``curio``, ``trio``, or any other tool.
    Internally we use ``anyio`` to test
    that it works as expected for any io stack.

    Note that ``Future[a]`` represents a computation
    that never fails and returns ``IO[a]`` type.
    Use ``FutureResult[a, b]`` for operations that might fail.
    Like DB access or network operations.

    Is not related to ``asyncio.Future`` in any kind.

    Tradeoffs
    ---------

    Due to possible performance issues we move all coroutines definitions
    to a separate module.

    See also:
        https://gcanti.github.io/fp-ts/modules/Task.ts.html
        https://zio.dev/docs/overview/overview_basic_concurrency
        https://github.com/correl/typesafe-monads/blob/master/monads/future.py

    """

    _inner_value: Awaitable[_ValueType]

    def __init__(self, inner_value: Awaitable[_ValueType]) -> None:
        """
        Public constructor for this type. Also required for typing.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> async def coro(arg: int) -> int:
          ...     return arg + 1
          ...
          >>> container = Future(coro(1))
          >>> assert anyio.run(container.awaitable) == IO(2)

        """
        super().__init__(inner_value)

    def __await__(self) -> Generator[Any, Any, IO[_ValueType]]:
        """
        By defining this magic method we make ``Future`` awaitable.

        This means you can use ``await`` keyword to evaluate this container:

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> async def main() -> IO[int]:
          ...     return await Future.from_value(1)
          ...
          >>> assert anyio.run(main) == IO(1)

        When awaited we returned the value wrapped
        in :class:`returns.io.IO` container
        to indicate that the computation was impure.

        See also:
            https://docs.python.org/3/library/asyncio-task.html#awaitables
            https://www.python.org/dev/peps/pep-0492/#new-abstract-base-classes

        """
        return self.awaitable().__await__()  # noqa: WPS609

    async def awaitable(self) -> IO[_ValueType]:
        """
        Transforms ``Future[a]`` to ``Awaitable[IO[a]]``.

        Use this method when you need a real coroutine.
        Like for ``asyncio.run`` calls.

        Note, that returned value will be wrapped
        in :class:`returns.io.IO` container.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO
          >>> assert anyio.run(Future.from_value(1).awaitable) == IO(1)

        """
        return IO(await self._inner_value)

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Future[_NewValueType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the IO instance
        and returns a new ``Future`` object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> def mappable(x: int) -> int:
          ...    return x + 1
          ...
          >>> assert anyio.run(
          ...     Future.from_value(1).map(mappable).awaitable,
          ... ) == IO(2)

        """
        return Future(_future.async_map(function, self._inner_value))

    def bind(
        self,
        function: Callable[[_ValueType], 'Future[_NewValueType]'],
    ) -> 'Future[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return ``Future`` type object.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> def bindable(x: int) -> Future[int]:
          ...    return Future.from_value(x + 1)
          ...
          >>> assert anyio.run(
          ...     Future.from_value(1).bind(bindable).awaitable,
          ... ) == IO(2)

        """
        return Future(_future.async_bind(function, self._inner_value))

    def bind_async(
        self,
        function: Callable[[_ValueType], Awaitable['Future[_NewValueType]']],
    ) -> 'Future[_NewValueType]':
        """
        Compose a container and ``async`` function returning a container.

        This function should return a container value.
        See :meth:`~Future.bind_awaitable`
        to bind ``async`` function that returns a plain value.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> async def coroutine(x: int) -> Future[str]:
          ...    return Future.from_value(str(x + 1))
          ...
          >>> assert anyio.run(
          ...     Future.from_value(1).bind_async(coroutine).awaitable,
          ... ) == IO('2')

        """
        return Future(_future.async_bind_async(function, self._inner_value))

    def bind_awaitable(
        self,
        function: Callable[[_ValueType], 'Awaitable[_NewValueType]'],
    ) -> 'Future[_NewValueType]':
        """
        Allows to compose a container and a regular ``async`` function.

        This function should return plain, non-container value.
        See :meth:`~Future.bind_async`
        to bind ``async`` function that returns a container.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> async def coroutine(x: int) -> int:
          ...    return x + 1
          ...
          >>> assert anyio.run(
          ...     Future.from_value(1).bind_awaitable(coroutine).awaitable,
          ... ) == IO(2)

        """
        return Future(_future.async_bind_awaitable(
            function, self._inner_value,
        ))

    def bind_io(
        self,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> 'Future[_NewValueType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return ``IO`` type object.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> def bindable(x: int) -> IO[int]:
          ...    return IO(x + 1)
          ...
          >>> assert anyio.run(
          ...     Future.from_value(1).bind_io(bindable).awaitable,
          ... ) == IO(2)

        """
        return Future(_future.async_bind_io(function, self._inner_value))

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[['Future[_ValueType]'], 'Future[_NewValueType]']:
        """
        Lifts function to be wrapped in ``Future`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b`` to: ``Future[a] -> Future[b]``

        Works similar to :meth:`~Future.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not Future!
          ...
          >>> async def main() -> Future[float]:
          ...     return await Future.lift(example)(Future.from_value(1))
          ...
          >>> assert anyio.run(main) == IO(0.5)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def lift_io(
        cls,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> Callable[['Future[_ValueType]'], 'Future[_NewValueType]']:
        """
        Lifts IO function to be wrapped in ``Future`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> IO[b]`` to: ``Future[a] -> Future[b]``

        Works similar to :meth:`~Future.bind_io`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> def example(argument: int) -> IO[float]:
          ...     return IO(argument / 2)
          ...
          >>> async def main() -> Future[float]:
          ...     container = Future.from_value(1)
          ...     return await Future.lift_io(example)(container)
          ...
          >>> assert anyio.run(main) == IO(0.5)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.bind_io(function)

    @classmethod
    def from_value(cls, inner_value: _NewValueType) -> 'Future[_NewValueType]':
        """
        Allows to create a ``Future`` from a plain value.

        The resulting ``Future`` will just return the given value
        wrapped in :class:`returns.io.IO` container when awaited.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future
          >>> from returns.io import IO

          >>> async def main() -> bool:
          ...    return (await Future.from_value(1)) == IO(1)
          ...
          >>> assert anyio.run(main) is True

        """
        return Future(async_identity(inner_value))

    @classmethod
    def from_futureresult(
        cls,
        container: 'FutureResult[_ValueType, _ErrorType]',
    ) -> 'Future[Result[_ValueType, _ErrorType]]':
        """
        Creates ``Future[Result[a, b]]`` instance from ``FutureResult[a, b]``.

        This method is the inverse of :meth:`~FutureResult.from_typecast`.

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future, FutureResult
          >>> from returns.io import IO
          >>> from returns.result import Success

          >>> container = Future.from_futureresult(FutureResult.from_success(1))
          >>> assert anyio.run(container.awaitable) == IO(Success(1))

        """
        return Future(container._inner_value)


# Decorators:

def future(
    function: Callable[
        ...,
        Coroutine[_FirstType, _SecondType, _ValueType],
    ],
) -> Callable[..., Future[_ValueType]]:
    """
    Decorator to turn a coroutine definition into ``Future`` container.

    .. code:: python

      >>> import anyio
      >>> from returns.io import IO
      >>> from returns.future import future

      >>> @future
      ... async def test(x: int) -> int:
      ...     return x + 1
      ...
      >>> assert anyio.run(test(1).awaitable) == IO(2)

    """
    @wraps(function)
    def decorator(*args, **kwargs):
        return Future(function(*args, **kwargs))
    return decorator


# FutureResult
# ============

@final
class FutureResult(BaseContainer, Generic[_ValueType, _ErrorType]):
    """
    Container to easily compose ``async`` functions.

    Represents a better abstraction over a simple coroutine.

    Is framework, event-loop, and IO-library agnostics.
    Works with ``asyncio``, ``curio``, ``trio``, or any other tool.
    Internally we use ``anyio`` to test
    that it works as expected for any io stack.

    Note that ``FutureResult[a, b]`` represents a computation
    that can fail and returns ``IOResult[a, b]`` type.
    Use ``Future[a]`` for operations that cannot fail.

    This is a ``Future`` that returns ``Result`` type.
    By providing this utility type we make developers' lifes easier.
    ``FutureResult`` has a lot of composition helpers
    to turn complex nested operations into a one function calls.

    Tradeoffs
    ---------

    Due to possible performance issues we move all coroutines definitions
    to a separate module.

    See also:
        https://gcanti.github.io/fp-ts/modules/TaskEither.ts.html
        https://zio.dev/docs/overview/overview_basic_concurrency


    """

    _inner_value: Awaitable[Result[_ValueType, _ErrorType]]

    def __init__(
        self,
        inner_value: Awaitable[Result[_ValueType, _ErrorType]],
    ) -> None:
        """
        Public constructor for this type. Also required for typing.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess
          >>> from returns.result import Success, Result

          >>> async def coro(arg: int) -> Result[int, str]:
          ...     return Success(arg + 1)
          ...
          >>> container = FutureResult(coro(1))
          >>> assert anyio.run(container.awaitable) == IOSuccess(2)

        """
        super().__init__(inner_value)

    def __await__(self) -> Generator[
        Any, Any, IOResult[_ValueType, _ErrorType],
    ]:
        """
        By defining this magic method we make ``FutureResult`` awaitable.

        This means you can use ``await`` keyword to evaluate this container:

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOResult

          >>> async def main() -> IOResult[int, str]:
          ...     return await FutureResult.from_success(1)
          ...
          >>> assert anyio.run(main) == IOSuccess(1)

        When awaited we returned the value wrapped
        in :class:`returns.io.IOResult` container
        to indicate that the computation was impure and can fail.

        See also:
            https://docs.python.org/3/library/asyncio-task.html#awaitables
            https://www.python.org/dev/peps/pep-0492/#new-abstract-base-classes

        """
        return self.awaitable().__await__()  # noqa: WPS609

    async def awaitable(self) -> IOResult[_ValueType, _ErrorType]:
        """
        Transforms ``FutureResult[a, b]`` to ``Awaitable[IOResult[a, b]]``.

        Use this method when you need a real coroutine.
        Like for ``asyncio.run`` calls.

        Note, that returned value will be wrapped
        in :class:`returns.io.IOResult` container.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess
          >>> assert anyio.run(
          ...     FutureResult.from_success(1).awaitable,
          ... ) == IOSuccess(1)

        """
        return IOResult.from_result(await self._inner_value)

    def map(  # noqa: WPS125
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Applies function to the inner value.

        Applies 'function' to the contents of the IO instance
        and returns a new ``FutureResult`` object containing the result.
        'function' should accept a single "normal" (non-container) argument
        and return a non-container result.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def mappable(x: int) -> int:
          ...    return x + 1
          ...
          >>> assert anyio.run(
          ...     FutureResult.from_success(1).map(mappable).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).map(mappable).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_map(
            function, self._inner_value,
        ))

    def bind(
        self,
        function: Callable[
            [_ValueType],
            'FutureResult[_NewValueType, _ErrorType]',
        ],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Applies 'function' to the result of a previous calculation.

        'function' should accept a single "normal" (non-container) argument
        and return ``Future`` type object.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def bindable(x: int) -> FutureResult[int, str]:
          ...    return FutureResult.from_success(x + 1)
          ...
          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind(bindable).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).bind(bindable).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_bind(
            function, self._inner_value,
        ))

    def bind_async(
        self,
        function: Callable[
            [_ValueType],
            Awaitable['FutureResult[_NewValueType, _ErrorType]'],
        ],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Composes a container and ``async`` function returning container.

        This function should return a container value.
        See :meth:`~FutureResult.bind_awaitable`
        to bind ``async`` function that returns a plain value.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def coroutine(x: int) -> FutureResult[str, int]:
          ...    return FutureResult.from_success(str(x + 1))

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_async(coroutine).awaitable,
          ... ) == IOSuccess('2')
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).bind_async(coroutine).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_bind_async(
            function, self._inner_value,
        ))

    def bind_awaitable(
        self,
        function: Callable[[_ValueType], Awaitable[_NewValueType]],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Allows to compose a container and a regular ``async`` function.

        This function should return plain, non-container value.
        See :meth:`~FutureResult.bind_async`
        to bind ``async`` function that returns a container.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> async def coro(x: int) -> int:
          ...    return x + 1

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_awaitable(coro).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).bind_awaitable(coro).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_bind_awaitable(
            function, self._inner_value,
        ))

    def bind_result(
        self,
        function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Binds a function returning ``Result[a, b]`` container.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Result, Success
          >>> from returns.future import FutureResult

          >>> def bind(inner_value: int) -> Result[int, str]:
          ...     return Success(inner_value + 1)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_result(bind).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure('a').bind_result(bind).awaitable,
          ... ) == IOFailure('a')

        """
        return FutureResult(_future_result.async_bind_result(
            function, self._inner_value,
        ))

    def bind_ioresult(
        self,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Binds a function returning ``IOResult[a, b]`` container.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOResult, IOSuccess, IOFailure
          >>> from returns.future import FutureResult

          >>> def bind(inner_value: int) -> IOResult[int, str]:
          ...     return IOSuccess(inner_value + 1)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_ioresult(bind).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure('a').bind_ioresult(bind).awaitable,
          ... ) == IOFailure('a')

        """
        return FutureResult(_future_result.async_bind_ioresult(
            function, self._inner_value,
        ))

    def bind_io(
        self,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Binds a function returning ``IO[a]`` container.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IO, IOSuccess, IOFailure
          >>> from returns.future import FutureResult

          >>> def bind(inner_value: int) -> IO[float]:
          ...     return IO(inner_value + 0.5)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_io(bind).awaitable,
          ... ) == IOSuccess(1.5)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).bind_io(bind).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_bind_io(
            function, self._inner_value,
        ))

    def bind_future(
        self,
        function: Callable[[_ValueType], Future[_NewValueType]],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Binds a function returning ``Future[a]`` container.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.future import Future, FutureResult

          >>> def bind(inner_value: int) -> Future[float]:
          ...     return Future.from_value(inner_value + 0.5)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).bind_future(bind).awaitable,
          ... ) == IOSuccess(1.5)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).bind_future(bind).awaitable,
          ... ) == IOFailure(1)

        """
        return FutureResult(_future_result.async_bind_future(
            function, self._inner_value,
        ))

    def unify(
        self,
        function: Callable[
            [_ValueType], 'FutureResult[_NewValueType, _NewErrorType]',
        ],
    ) -> 'FutureResult[_NewValueType, Union[_ErrorType, _NewErrorType]]':
        """
        Composes successful container with a function that returns a container.

        Similar to :meth:`~FutureResult.bind` but has different type.
        It returns ``FutureResult[ValueType, Union[ErrorType, NewErrorType]]``
        instead of ``FutureResult[ValueType, ErrorType]``.

        So, it can be more useful in some situations.
        Probably with specific exceptions.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def bindable(x: int) -> FutureResult[int, str]:
          ...    return FutureResult.from_success(x + 1)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).unify(bindable).awaitable,
          ... ) == IOSuccess(2)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).unify(bindable).awaitable,
          ... ) == IOFailure(1)

        """
        return self.bind(function)  # type: ignore

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'FutureResult[_NewValueType, _ErrorType]':
        """
        Composes failed container with a pure function to fix the failure.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess

          >>> def fixable(arg: int) -> int:
          ...      return arg + 1

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).fix(fixable).awaitable,
          ... ) == IOSuccess(1)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).fix(fixable).awaitable,
          ... ) == IOSuccess(2)

        """
        return FutureResult(_future_result.async_fix(
            function, self._inner_value,
        ))

    def alt(
        self,
        function: Callable[[_ErrorType], _NewErrorType],
    ) -> 'FutureResult[_ValueType, _NewErrorType]':
        """
        Composes failed container with a pure function to modify failure.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def fixable(arg: int) -> int:
          ...      return arg + 1

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).alt(fixable).awaitable,
          ... ) == IOSuccess(1)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).alt(fixable).awaitable,
          ... ) == IOFailure(2)

        """
        return FutureResult(_future_result.async_alt(
            function, self._inner_value,
        ))

    def rescue(
        self,
        function: Callable[
            [_ErrorType],
            'FutureResult[_ValueType, _NewErrorType]',
        ],
    ) -> 'FutureResult[_ValueType, _NewErrorType]':
        """
        Composes failed container with a function that returns a container.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess

          >>> def rescuable(x: int) -> FutureResult[int, str]:
          ...    return FutureResult.from_success(x + 1)

          >>> assert anyio.run(
          ...     FutureResult.from_success(1).rescue(rescuable).awaitable,
          ... ) == IOSuccess(1)
          >>> assert anyio.run(
          ...     FutureResult.from_failure(1).rescue(rescuable).awaitable,
          ... ) == IOSuccess(2)

        """
        return FutureResult(_future_result.async_rescue(
            function, self._inner_value,
        ))

    async def value_or(
        self,
        default_value: _NewValueType,
    ) -> IO[Union[_ValueType, _NewValueType]]:
        """
        Get value or default value.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IO

          >>> async def main():
          ...     first = await FutureResult.from_success(1).value_or(2)
          ...     second = await FutureResult.from_failure(3).value_or(4)
          ...     return first, second

          >>> assert anyio.run(main) == (IO(1), IO(4))

        """
        return IO((await self._inner_value).value_or(default_value))

    async def unwrap(self) -> IO[_ValueType]:
        """
        Get value or raise exception.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IO
          >>> assert anyio.run(FutureResult.from_success(1).unwrap) == IO(1)

        .. code::

          >>> anyio.run(FutureResult.from_failure(1).unwrap)
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return IO((await self._inner_value).unwrap())

    async def failure(self) -> IO[_ErrorType]:
        """
        Get failed value or raise exception.

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IO
          >>> assert anyio.run(FutureResult.from_failure(1).failure) == IO(1)

        .. code::

          >>> anyio.run(FutureResult.from_success(1).failure)
          Traceback (most recent call last):
            ...
          returns.primitives.exceptions.UnwrapFailedError

        """
        return IO((await self._inner_value).failure())

    @classmethod
    def lift(
        cls,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Callable[
        ['FutureResult[_ValueType, _ContraErrorType]'],
        'FutureResult[_NewValueType, _ContraErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``FutureResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> b``
        to: ``FutureResult[a, x] -> FutureResult[b, x]``

        Works similar to :meth:`~FutureResult.map`, but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def example(argument: int) -> float:
          ...     return argument / 2  # not FutureResult!
          ...
          >>> async def success() -> FutureResult[float, int]:
          ...     container = FutureResult.from_success(1)
          ...     return await FutureResult.lift(example)(container)
          ...
          >>> async def failure() -> FutureResult[float, int]:
          ...     container = FutureResult.from_failure(1)
          ...     return await FutureResult.lift(example)(container)
          ...

          >>> assert anyio.run(success) == IOSuccess(0.5)
          >>> assert anyio.run(failure) == IOFailure(1)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

    @classmethod
    def lift_result(
        cls,
        function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    ) -> Callable[
        ['FutureResult[_ValueType, _ErrorType]'],
        'FutureResult[_NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``FutureResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> Result[b, x]``
        to: ``FutureResult[a, x] -> FutureResult[b, x]``

        Works similar to :meth:`~FutureResult.bind_result`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Result, Success

          >>> def example(argument: int) -> Result[float, int]:
          ...     return Success(argument / 2)
          ...
          >>> async def success() -> FutureResult[float, int]:
          ...     container = FutureResult.from_success(1)
          ...     return await FutureResult.lift_result(example)(container)
          ...
          >>> async def failure() -> FutureResult[float, int]:
          ...     container = FutureResult.from_failure(1)
          ...     return await FutureResult.lift_result(example)(container)
          ...

          >>> assert anyio.run(success) == IOSuccess(0.5)
          >>> assert anyio.run(failure) == IOFailure(1)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.bind_result(function)

    @classmethod
    def lift_io(
        cls,
        function: Callable[[_ValueType], IO[_NewValueType]],
    ) -> Callable[
        ['FutureResult[_ValueType, _ContraErrorType]'],
        'FutureResult[_NewValueType, _ContraErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``FutureResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> IO[b]``
        to: ``FutureResult[a, x] -> FutureResult[b, x]``

        Works similar to :meth:`~FutureResult.bind_io`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IO, IOSuccess, IOFailure

          >>> def example(argument: int) -> IO[float]:
          ...     return IO(argument / 2)
          ...
          >>> async def success() -> FutureResult[float, int]:
          ...     container = FutureResult.from_success(1)
          ...     return await FutureResult.lift_io(example)(container)
          ...
          >>> async def failure() -> FutureResult[float, int]:
          ...     container = FutureResult.from_failure(1)
          ...     return await FutureResult.lift_io(example)(container)
          ...

          >>> assert anyio.run(success) == IOSuccess(0.5)
          >>> assert anyio.run(failure) == IOFailure(1)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.bind_io(function)

    @classmethod
    def lift_ioresult(
        cls,
        function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    ) -> Callable[
        ['FutureResult[_ValueType, _ErrorType]'],
        'FutureResult[_NewValueType, _ErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``FutureResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> IOResult[b, x]``
        to: ``FutureResult[a, x] -> FutureResult[b, x]``

        Works similar to :meth:`~FutureResult.bind_result`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import FutureResult
          >>> from returns.io import IOSuccess, IOFailure, IOResult

          >>> def example(argument: int) -> IOResult[float, int]:
          ...     return IOSuccess(argument / 2)
          ...
          >>> async def success() -> FutureResult[float, int]:
          ...     container = FutureResult.from_success(1)
          ...     return await FutureResult.lift_ioresult(example)(container)
          ...
          >>> async def failure() -> FutureResult[float, int]:
          ...     container = FutureResult.from_failure(1)
          ...     return await FutureResult.lift_ioresult(example)(container)
          ...

          >>> assert anyio.run(success) == IOSuccess(0.5)
          >>> assert anyio.run(failure) == IOFailure(1)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.bind_ioresult(function)

    @classmethod
    def lift_future(
        cls,
        function: Callable[[_ValueType], Future[_NewValueType]],
    ) -> Callable[
        ['FutureResult[_ValueType, _ContraErrorType]'],
        'FutureResult[_NewValueType, _ContraErrorType]',
    ]:
        """
        Lifts function to be wrapped in ``FutureResult`` for better composition.

        In other words, it modifies the function's
        signature from: ``a -> Future[b]``
        to: ``FutureResult[a, x] -> FutureResult[b, x]``

        Works similar to :meth:`~FutureResult.bind_future`,
        but has inverse semantics.

        This is how it should be used:

        .. code:: python

          >>> import anyio
          >>> from returns.future import Future, FutureResult
          >>> from returns.io import IOSuccess, IOFailure

          >>> def example(argument: int) -> Future[float]:
          ...     return Future.from_value(argument / 2)
          ...
          >>> async def success() -> FutureResult[float, int]:
          ...     container = FutureResult.from_success(1)
          ...     return await FutureResult.lift_future(example)(container)
          ...
          >>> async def failure() -> FutureResult[float, int]:
          ...     container = FutureResult.from_failure(1)
          ...     return await FutureResult.lift_future(example)(container)
          ...

          >>> assert anyio.run(success) == IOSuccess(0.5)
          >>> assert anyio.run(failure) == IOFailure(1)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.bind_future(function)

    @classmethod
    def from_typecast(
        cls,
        container: Future[Result[_NewValueType, _NewErrorType]],
    ) -> 'FutureResult[_NewValueType, _NewErrorType]':
        """
        Creates ``FutureResult[a, b]`` from ``Future[Result[a, b]]``.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Success, Failure
          >>> from returns.future import Future, FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_typecast(
          ...         Future.from_value(Success(1)),
          ...     ) == IOSuccess(1)
          ...     assert await FutureResult.from_typecast(
          ...         Future.from_value(Failure(1)),
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult(container._inner_value)

    @classmethod
    def from_successful_future(
        cls,
        container: Future[_NewValueType],
    ) -> 'FutureResult[_NewValueType, Any]':
        """
        Creates ``FutureResult`` from successful ``Future`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess
          >>> from returns.future import Future, FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_successful_future(
          ...         Future.from_value(1),
          ...     ) == IOSuccess(1)

          >>> anyio.run(main)

        """
        return FutureResult(_future_result.async_success(container))

    @classmethod
    def from_failed_future(
        cls,
        container: Future[_NewErrorType],
    ) -> 'FutureResult[Any, _NewErrorType]':
        """
        Creates ``FutureResult`` from failed ``Future`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOFailure
          >>> from returns.future import Future, FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_failed_future(
          ...         Future.from_value(1),
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult(_future_result.async_failure(container))

    @classmethod
    def from_successful_io(
        cls,
        container: IO[_NewValueType],
    ) -> 'FutureResult[_NewValueType, Any]':
        """
        Creates ``FutureResult`` from successful ``IO`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IO, IOSuccess
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_successful_io(
          ...         IO(1),
          ...     ) == IOSuccess(1)

          >>> anyio.run(main)

        """
        return FutureResult.from_success(container._inner_value)

    @classmethod
    def from_failed_io(
        cls,
        container: IO[_NewErrorType],
    ) -> 'FutureResult[Any, _NewErrorType]':
        """
        Creates ``FutureResult`` from failed ``IO`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IO, IOFailure
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_failed_io(
          ...         IO(1),
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult.from_failure(container._inner_value)

    @classmethod
    def from_ioresult(
        cls,
        container: IOResult[_NewValueType, _NewErrorType],
    ) -> 'FutureResult[_NewValueType, _NewErrorType]':
        """
        Creates ``FutureResult`` from ``IOResult`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_ioresult(
          ...         IOSuccess(1),
          ...     ) == IOSuccess(1)
          ...     assert await FutureResult.from_ioresult(
          ...         IOFailure(1),
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult(async_identity(container._inner_value))

    @classmethod
    def from_result(
        cls,
        container: Result[_NewValueType, _NewErrorType],
    ) -> 'FutureResult[_NewValueType, _NewErrorType]':
        """
        Creates ``FutureResult`` from ``Result`` value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess, IOFailure
          >>> from returns.result import Success, Failure
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_result(
          ...         Success(1),
          ...     ) == IOSuccess(1)
          ...     assert await FutureResult.from_result(
          ...         Failure(1),
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult(async_identity(container))

    @classmethod
    def from_success(
        cls,
        inner_value: _NewValueType,
    ) -> 'FutureResult[_NewValueType, Any]':
        """
        Creates ``FutureResult`` from successful value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOSuccess
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_success(
          ...         1,
          ...     ) == IOSuccess(1)

          >>> anyio.run(main)

        """
        return FutureResult(async_identity(Success(inner_value)))

    @classmethod
    def from_failure(
        cls,
        inner_value: _NewErrorType,
    ) -> 'FutureResult[Any, _NewErrorType]':
        """
        Creates ``FutureResult`` from failed value.

        .. code:: python

          >>> import anyio
          >>> from returns.io import IOFailure
          >>> from returns.future import FutureResult

          >>> async def main():
          ...     assert await FutureResult.from_failure(
          ...         1,
          ...     ) == IOFailure(1)

          >>> anyio.run(main)

        """
        return FutureResult(async_identity(Failure(inner_value)))


# Aliases:

#: Alias for a popular case when ``Result`` has ``Exception`` as error type.
FutureResultE = FutureResult[_ValueType, Exception]


# Decorators:

def future_safe(
    function: Callable[..., Coroutine[_FirstType, _SecondType, _ValueType]],
) -> Callable[..., FutureResultE[_ValueType]]:
    """
    Decorator to convert exception-throwing coroutine to ``FutureResult``.

    Should be used with care, since it only catches ``Exception`` subclasses.
    It does not catch ``BaseException`` subclasses.

    If you need to mark sync function as ``safe``,
    use :func:`returns.future.future_safe` instead.
    This decorator only works with ``async`` functions. Example:

    .. code:: python

      >>> import anyio
      >>> from returns.future import future_safe
      >>> from returns.io import IOSuccess, IOResult

      >>> @future_safe
      ... async def might_raise(arg: int) -> float:
      ...     return 1 / arg
      ...

      >>> assert anyio.run(might_raise(2).awaitable) == IOSuccess(0.5)
      >>> assert isinstance(
      ...     anyio.run(might_raise(0).awaitable),
      ...     IOResult.failure_type,
      ... )

    Similar to :func:`returns.io.impure_safe` and :func:`returns.result.safe`
    decorators, but works with ``async`` functions.

    """
    async def factory(*args, **kwargs) -> Result[_ValueType, Exception]:
        try:
            return Success(await function(*args, **kwargs))
        except Exception as exc:
            return Failure(exc)

    @wraps(function)
    def decorator(*args, **kwargs):
        return FutureResult(factory(*args, **kwargs))
    return decorator
