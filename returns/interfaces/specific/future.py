from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, NoReturn, Type, TypeVar, Generator, Awaitable, Coroutine

from returns.interfaces.async_ import AsyncLikeN
from returns.interfaces.specific import io
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.future import Future  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_FutureLikeType = TypeVar('_FutureLikeType', bound='FutureLikeN')
_FutureBasedType = TypeVar('_FutureBasedType', bound='FutureBasedN')


class FutureLikeN(io.IOBasedN[_FirstType, _SecondType, _ThirdType]):
    """
    Represents the base interfaces for types that do fearless async operations.

    This type means that ``Future`` cannot fail.
    Don't use this type for async that can. Instead, use
    :class:`returns.interfaces.specific.future_result.FutureResultBasedN` type.

    """

    @abstractmethod
    def bind_future(
        self: _FutureLikeType,
        function: Callable[[_FirstType], 'Future[_UpdatedType]'],
    ) -> KindN[_FutureLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a container."""

    @abstractmethod
    def bind_async(
        self: _FutureLikeType,
        function: Callable[
            [_FirstType],
            Awaitable[
                KindN[_FutureLikeType, _UpdatedType, _SecondType, _ThirdType],
            ],
        ],
    ) -> KindN[_FutureLikeType, _UpdatedType, _SecondType, _ThirdType]:
        ...

    @classmethod
    @abstractmethod
    def from_future(
        cls: Type[_FutureLikeType],  # noqa: N805
        inner_value: 'Future[_FirstType]',
    ) -> KindN[_FutureLikeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from successful ``IO``."""


#: Type alias for kinds with one type argument.
FutureLike1 = FutureLikeN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
FutureLike2 = FutureLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
FutureLike3 = FutureLikeN[_FirstType, _SecondType, _ThirdType]


class FutureBasedN(
    FutureLikeN[_FirstType, _SecondType, _ThirdType],
    AsyncLikeN[_FirstType, _SecondType, _ThirdType],
):
    ...


#: Type alias for kinds with one type argument.
FutureBased1 = FutureBasedN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
FutureBased2 = FutureBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
FutureBased3 = FutureBasedN[_FirstType, _SecondType, _ThirdType]
