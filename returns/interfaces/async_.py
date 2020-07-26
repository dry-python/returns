from abc import abstractmethod
from typing import Any, Callable, NoReturn, Type, TypeVar, Generator, Awaitable, Coroutine, Generic

from returns.interfaces.specific import io
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_AsyncLikeType = TypeVar('_AsyncLikeType', bound='AsyncLikeN')


class AsyncLikeN(Generic[_FirstType, _SecondType, _ThirdType]):

    @abstractmethod
    def __await__(self: _AsyncLikeType) -> Generator[
        Any,
        Any,
        io.IOBasedN[_FirstType, _SecondType, _ThirdType],
    ]:
        ...

    @abstractmethod
    async def awaitable(
        self: _AsyncLikeType,
    ) -> io.IOBasedN[_FirstType, _SecondType, _ThirdType]:
        ...


#: Type alias for kinds with one type argument.
AsyncLike1 = AsyncLikeN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
AsyncLike2 = AsyncLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
AsyncLike3 = AsyncLikeN[_FirstType, _SecondType, _ThirdType]
