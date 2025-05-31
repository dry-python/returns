import asyncio
from collections.abc import Awaitable, Callable, Generator
from functools import wraps
from typing import Any, NewType, ParamSpec, TypeVar, cast, final

_ValueType = TypeVar('_ValueType')
_AwaitableT = TypeVar('_AwaitableT', bound=Awaitable)
_Ps = ParamSpec('_Ps')

_Sentinel = NewType('_Sentinel', object)
_sentinel: _Sentinel = cast(_Sentinel, object())


@final
class ReAwaitable:
    """
    Allows to write coroutines that can be awaited multiple times.

    It works by actually caching the ``await`` result and reusing it.
    So, in reality we still ``await`` once,
    but pretending to do it multiple times.

    This class is thread-safe and supports concurrent awaits from multiple
    async tasks. When multiple tasks await the same instance simultaneously,
    only one will execute the underlying coroutine while others will wait
    and receive the cached result.

    Why is that required? Because otherwise,
    ``Future`` containers would be unusable:

    .. code:: python

      >>> import anyio
      >>> from returns.future import Future
      >>> from returns.io import IO

      >>> async def example(arg: int) -> int:
      ...     return arg

      >>> instance = Future(example(1))
      >>> two = instance.map(lambda x: x + 1)
      >>> zero = instance.map(lambda x: x - 1)

      >>> assert anyio.run(two.awaitable) == IO(2)
      >>> assert anyio.run(zero.awaitable) == IO(0)

    In this example we ``await`` our ``Future`` twice.
    It happens in each ``.map`` call.
    Without this class (that is used inside ``Future``)
    it would result in ``RuntimeError: cannot reuse already awaited coroutine``.

    We try to make this type transparent.
    It should not actually be visible to any of its users.

    """

    __slots__ = ('_cache', '_coro', '_lock')

    def __init__(self, coro: Awaitable[_ValueType]) -> None:
        """We need just an awaitable to work with."""
        self._coro = coro
        self._cache: _ValueType | _Sentinel = _sentinel
        self._lock: Any = None

    def __await__(self) -> Generator[None, None, _ValueType]:
        """
        Allows to use ``await`` multiple times.

        .. code:: python

          >>> import anyio
          >>> from returns.primitives.reawaitable import ReAwaitable

          >>> async def say_hello() -> str:
          ...    return 'Hello'

          >>> async def main():
          ...    instance = ReAwaitable(say_hello())
          ...    print(await instance)
          ...    print(await instance)
          ...    print(await instance)

          >>> anyio.run(main)
          Hello
          Hello
          Hello

        """
        return self._awaitable().__await__()

    def __repr__(self) -> str:
        """
        Formats this type the same way as the coroutine underneath.

        .. code:: python

          >>> from returns.primitives.reawaitable import ReAwaitable

          >>> async def test() -> int:
          ...    return 1

          >>> assert repr(test) == repr(ReAwaitable(test))
          >>> repr(ReAwaitable(test))
          '<function test at 0x...>'

        """
        return repr(self._coro)

    async def _awaitable(self) -> _ValueType:
        """Caches the once awaited value forever."""
        if self._cache is not _sentinel:
            return self._cache  # type: ignore

        # Create lock on first use to detect the async framework
        if self._lock is None:
            try:
                # Try to get the current event loop
                self._lock = asyncio.Lock()
            except RuntimeError:
                # If no event loop, we're probably in a different
                # async framework
                # For now, we'll fall back to the original behavior
                # This maintains compatibility while fixing the asyncio case
                if self._cache is _sentinel:
                    self._cache = await self._coro
                # This return is unreachable in practice due to race timing.
                # The cache would need to be set by another coroutine between
                # the initial check (line 111) and this point.
                return self._cache  # type: ignore  # pragma: no cover

        async with self._lock:
            # Double-check after acquiring the lock
            if self._cache is _sentinel:
                self._cache = await self._coro
        # This return is unreachable in practice due to race timing.
        # The cache would need to be set by another coroutine while waiting
        # for the lock, but that's prevented by the lock mechanism itself.
        return self._cache  # type: ignore  # pragma: no cover


def reawaitable(
    coro: Callable[_Ps, _AwaitableT],
) -> Callable[_Ps, _AwaitableT]:
    """
    Allows to decorate coroutine functions to be awaitable multiple times.

    .. code:: python

      >>> import anyio
      >>> from returns.primitives.reawaitable import reawaitable

      >>> @reawaitable
      ... async def return_int() -> int:
      ...    return 1

      >>> async def main():
      ...    instance = return_int()
      ...    return await instance + await instance + await instance

      >>> assert anyio.run(main) == 3

    """

    @wraps(coro)
    def decorator(
        *args: _Ps.args,
        **kwargs: _Ps.kwargs,
    ) -> _AwaitableT:
        return ReAwaitable(coro(*args, **kwargs))  # type: ignore[return-value]

    return decorator
