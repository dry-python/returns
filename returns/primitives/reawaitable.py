from collections.abc import Awaitable, Callable, Generator
from functools import wraps
from typing import Literal, NewType, ParamSpec, Protocol, TypeVar, cast, final
# Always import asyncio
import asyncio

# pragma: no cover
class AsyncLock(Protocol):
    """A protocol for an asynchronous lock."""
    def __init__(self) -> None: ...
    async def __aenter__(self) -> None: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...


# Define context types as literals
AsyncContext = Literal["asyncio", "trio", "unknown"]


# pragma: no cover
def _is_anyio_available() -> bool:
    """Check if anyio is available.

    Returns:
        bool: True if anyio is available
    """
    try:
        import anyio
    except ImportError:
        return False
    return True


# pragma: no cover
def _is_trio_available() -> bool:
    """Check if trio is available.

    Returns:
        bool: True if trio is available
    """
    if not _is_anyio_available():
        return False

    # pragma: no cover
    try:
        import trio
    except ImportError:
        return False
    return True


# Set availability flags at module level
has_anyio = _is_anyio_available()
has_trio = _is_trio_available()


def _is_in_trio_context() -> bool:
    """Check if we're in a trio context.

    Returns:
        bool: True if we're in a trio context
    """
    # Early return if trio is not available
    if not has_trio:
        return False
        
    # Import trio here since we already checked it's available
    import trio
    
    try:
        # Will raise RuntimeError if not in trio context
        trio.lowlevel.current_task()
    except (RuntimeError, AttributeError):
        # Not in a trio context or trio API changed
        return False
    return True


def detect_async_context() -> AsyncContext:
    """Detect which async context we're currently running in.

    Returns:
        AsyncContext: The current async context type
    """
    # This branch is only taken when anyio is not installed
    if not has_anyio or not _is_in_trio_context():
        return "asyncio"

    return "trio"


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

    Note:
        For proper trio support, the anyio library is required.
        If anyio is not available, we fall back to asyncio.Lock.

    """

    __slots__ = ('_cache', '_coro', '_lock')

    def __init__(self, coro: Awaitable[_ValueType]) -> None:
        """We need just an awaitable to work with."""
        self._coro = coro
        self._cache: _ValueType | _Sentinel = _sentinel
        self._lock: AsyncLock | None = None  # Will be created lazily based on the backend

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

    def _create_lock(self) -> AsyncLock:
        """Create the appropriate lock based on the current async context."""
        context = detect_async_context()

        if context == "trio" and has_anyio:
            try:
                import anyio
            except Exception:
                # Just continue to asyncio if anyio import fails
                return asyncio.Lock()
            return anyio.Lock()
                
        # For asyncio or unknown contexts
        return asyncio.Lock()

    async def _awaitable(self) -> _ValueType:
        """Caches the once awaited value forever."""
        # Create the lock if it doesn't exist
        if self._lock is None:
            self._lock = self._create_lock()

        try:
            async with self._lock:
                if self._cache is _sentinel:
                    self._cache = await self._coro
                return self._cache  # type: ignore
        except RuntimeError:  # pragma: no cover
            # Fallback for when running in asyncio context with trio detection
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

    Note:
        For proper trio support, the anyio library is required.
        If anyio is not available, we fall back to asyncio.Lock.
    """

    @wraps(coro)
    def decorator(
        *args: _Ps.args,
        **kwargs: _Ps.kwargs,
    ) -> _AwaitableT:
        return ReAwaitable(coro(*args, **kwargs))  # type: ignore[return-value]

    return decorator