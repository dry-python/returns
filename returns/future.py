from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Generator,
    Generic,
    TypeVar,
)

from typing_extensions import final

from returns.io import IO
from returns.primitives.container import BaseContainer

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
        Transforms ``Future[a]`` to ``Awaitable[a]``.

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
        and returns a new IO object containing the result.
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
        return Future(_async_map(function, self._inner_value))

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
        return Future(_async_bind(function, self._inner_value))

    def bind_async(
        self,
        function: Callable[[_ValueType], Awaitable['Future[_NewValueType]']],
    ) -> 'Future[_NewValueType]':
        """
        Allows to compose a container and ``async`` function.

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
        return Future(_async_bind_async(function, self._inner_value))

    def bind_awaitable(
        self,
        function: Callable[[_ValueType], 'Awaitable[_NewValueType]'],
    ) -> 'Future[_NewValueType]':
        """
        Allows to compose a container and ``async`` function.

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
        return Future(_async_bind_awaitable(function, self._inner_value))

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
          >>> async def main() -> IO[float]:
          ...     return await Future.lift(example)(Future.from_value(1))
          ...
          >>> assert anyio.run(main) == IO(0.5)

        See also:
            - https://wiki.haskell.org/Lifting
            - https://github.com/witchcrafters/witchcraft
            - https://en.wikipedia.org/wiki/Natural_transformation

        """
        return lambda container: container.map(function)

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


# Decorators:

def future(
    function: Callable[
        ...,
        Coroutine[_FirstType, _SecondType, _ValueType],
    ],
) -> Callable[..., Coroutine[_FirstType, _SecondType, Future[_ValueType]]]:
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


# Private composition helpers:

async def _async_map(
    function: Callable[[_ValueType], _NewValueType],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    return function(await inner_value)


async def _async_bind_awaitable(
    function: Callable[[_ValueType], Awaitable[_NewValueType]],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    return await function(await inner_value)


async def _async_bind(
    function: Callable[[_ValueType], 'Future[_NewValueType]'],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    return (await function(await inner_value))._inner_value  # noqa: WPS437


async def _async_bind_async(
    function: Callable[[_ValueType], Awaitable['Future[_NewValueType]']],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    inner_io = (await function(await inner_value))._inner_value  # noqa: WPS437
    return await inner_io
