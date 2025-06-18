import asyncio
import logging
import threading
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

    **Async Framework Support and Lock Selection:**

    The lock selection follows a strict priority order with automatic fallback:

    1. **asyncio.Lock()** - Primary choice when asyncio event loop available
    2. **trio.Lock()** - Used when asyncio fails and trio available
    3. **anyio.Lock()** - Used when asyncio/trio fail, anyio available
    4. **threading.Lock()** - Final fallback for unsupported frameworks

    Lock selection happens lazily on first await and is logged at DEBUG level
    for troubleshooting. The framework detection is automatic and transparent.

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
        self._lock: Any | None = None

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

    def _try_asyncio_lock(self, logger: logging.Logger) -> Any:
        """Try to create an asyncio lock."""
        try:
            asyncio_lock = asyncio.Lock()
        except RuntimeError:
            return None
        logger.debug('ReAwaitable: Using asyncio.Lock for concurrency control')
        return asyncio_lock

    def _try_trio_lock(self, logger: logging.Logger) -> Any:
        """Try to create a trio lock."""
        try:
            import trio  # noqa: PLC0415
        except ImportError:
            return None
        trio_lock = trio.Lock()
        logger.debug('ReAwaitable: Using trio.Lock for concurrency control')
        return trio_lock

    def _try_anyio_lock(self, logger: logging.Logger) -> Any:
        """Try to create an anyio lock."""
        try:
            import anyio  # noqa: PLC0415
        except ImportError:
            return None
        anyio_lock = anyio.Lock()
        logger.debug('ReAwaitable: Using anyio.Lock for concurrency control')
        return anyio_lock

    def _create_lock(self) -> Any:  # noqa: WPS320
        """Create appropriate lock for the current async framework.

        Attempts framework detection: asyncio -> trio -> anyio -> threading.
        Logs the selected framework at DEBUG level for troubleshooting.
        """
        logger = logging.getLogger(__name__)

        # Try asyncio first (most common)
        asyncio_lock = self._try_asyncio_lock(logger)
        if asyncio_lock is not None:
            return asyncio_lock

        logger.debug('ReAwaitable: asyncio.Lock unavailable, trying trio')

        # Try trio
        trio_lock = self._try_trio_lock(logger)
        if trio_lock is not None:
            return trio_lock

        logger.debug('ReAwaitable: trio.Lock unavailable, trying anyio')

        # Try anyio
        anyio_lock = self._try_anyio_lock(logger)
        if anyio_lock is not None:
            return anyio_lock

        logger.debug(
            'ReAwaitable: anyio.Lock unavailable, '
            'falling back to threading.Lock'
        )

        # Fallback to threading lock
        threading_lock = threading.Lock()
        logger.debug(
            'ReAwaitable: Using threading.Lock fallback for concurrency control'
        )
        return threading_lock

    async def _awaitable(self) -> _ValueType:
        """Caches the once awaited value forever."""
        if self._cache is not _sentinel:
            return self._cache  # type: ignore

        # Create lock on first use to detect the async framework
        if self._lock is None:
            self._lock = self._create_lock()

        # Handle different lock types
        if hasattr(self._lock, '__aenter__'):
            # Async lock (asyncio, trio, anyio)
            async with self._lock:
                if self._cache is _sentinel:
                    self._cache = await self._coro
        else:
            # Threading lock fallback for unsupported frameworks
            with self._lock:
                if self._cache is _sentinel:
                    self._cache = await self._coro

        return self._cache  # type: ignore


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
