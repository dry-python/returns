
from typing import Awaitable, Callable, Generator, NewType, TypeVar, Union, cast

from typing_extensions import final

_ValueType = TypeVar('_ValueType')
_FunctionCoroType = TypeVar('_FunctionCoroType', bound=Callable[..., Awaitable])

_Sentinel = NewType('_Sentinel', object)
_sentinel: _Sentinel = cast(_Sentinel, object())


@final
class ReAwaitable(object):
    """
    Allows to write coroutines that can be awaited multiple times.

    It works by actually caching the ``await`` result and reusing it.
    So, in reallity we still ``await`` once,
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

    """

    __slots__ = ('_coro', '_cache')

    def __init__(self, coro: Awaitable[_ValueType]) -> None:
        """We need just an awaitable to work with."""
        self._coro = coro
        self._cache: Union[_ValueType, _Sentinel] = _sentinel

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
        return self._awaitable().__await__()  # noqa: WPS609

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
        if self._cache is _sentinel:
            self._cache = await self._coro
        return self._cache  # type: ignore


def reawaitable(coro: _FunctionCoroType) -> _FunctionCoroType:
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
    return lambda *args, **kwargs: ReAwaitable(  # type: ignore
        coro(*args, **kwargs),
    )
