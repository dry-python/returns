
from typing import Awaitable, Callable, Generator, Optional, TypeVar

_ValueType = TypeVar('_ValueType')
_FunctionCoroType = TypeVar('_FunctionCoroType', bound=Callable[..., Awaitable])


class ReAwaitable(object):
    __slots__ = ('_coro', '_cache')

    def __init__(self, coro: Awaitable[_ValueType]) -> None:
        self._coro = coro
        self._cache: Optional[_ValueType] = None

    def __await__(self) -> Generator[None, None, _ValueType]:
        return self._awaitable().__await__()

    async def _awaitable(self) -> _ValueType:
        if self._cache is None:
            self._cache = await self._coro
        return self._cache


def reawaitable(coro: _FunctionCoroType) -> _FunctionCoroType:
    return lambda *args, **kwargs: ReAwaitable(  # type: ignore
        coro(*args, **kwargs),
    )
