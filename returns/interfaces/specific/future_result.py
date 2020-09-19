"""
Represents the base interfaces for types that do fear-some async operations.

This type means that ``FutureResult`` can (and will!) fail with exceptions.

Use this type to mark that this specific async opetaion can fail.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Awaitable, Callable, NoReturn, Type, TypeVar

from returns.interfaces.specific import future, ioresult
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.future import Future, FutureResult  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

_FutureResultLikeType = TypeVar(
    '_FutureResultLikeType', bound='FutureResultLikeN',
)


class FutureResultLikeN(
    future.FutureLikeN[_FirstType, _SecondType, _ThirdType],
    ioresult.IOResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    """
    Base type for ones that does look like ``FutureResult``.

    But at the time this is not a real ``Future`` and cannot be awaited.
    It is also cannot be unwrapped, because it is not a real ``IOResult``.
    """

    @abstractmethod
    def bind_future_result(
        self: _FutureResultLikeType,
        function: Callable[
            [_FirstType],
            'FutureResult[_UpdatedType, _SecondType]',
        ],
    ) -> KindN[_FutureResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to bind ``FutureResult`` functions over a container."""

    @abstractmethod
    def bind_async_future_result(
        self: _FutureResultLikeType,
        function: Callable[
            [_FirstType],
            Awaitable['FutureResult[_UpdatedType, _SecondType]'],
        ],
    ) -> KindN[_FutureResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to bind async ``FutureResult`` functions over container."""

    @classmethod
    @abstractmethod
    def from_failed_future(
        cls: Type[_FutureResultLikeType],  # noqa: N805
        inner_value: 'Future[_ErrorType]',
    ) -> KindN[_FutureResultLikeType, _FirstType, _ErrorType, _ThirdType]:
        """Creates new container from a failed ``Future``."""

    @classmethod
    def from_future_result(
        cls: Type[_FutureResultLikeType],  # noqa: N805
        inner_value: 'FutureResult[_ValueType, _ErrorType]',
    ) -> KindN[_FutureResultLikeType, _ValueType, _ErrorType, _ThirdType]:
        """Creates container from ``FutureResult`` instance."""


#: Type alias for kinds with two type arguments.
FutureResultLike2 = FutureResultLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
FutureResultLike3 = FutureResultLikeN[_FirstType, _SecondType, _ThirdType]


class FutureResultBasedN(
    future.FutureBasedN[_FirstType, _SecondType, _ThirdType],
    FutureResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    """
    Base type for real ``FutureResult`` objects.

    They can be awaited.
    Still cannot be unwrapped.
    """


#: Type alias for kinds with two type arguments.
FutureResultBased2 = FutureResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
FutureResultBased3 = FutureResultBasedN[_FirstType, _SecondType, _ThirdType]
