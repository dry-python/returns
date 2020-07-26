from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, NoReturn, Type, TypeVar

from returns.interfaces import (
    altable,
    applicative,
    bindable,
    mappable,
    rescuable,
    unwrappable,
)
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_FirstUnwrappableType = TypeVar('_FirstUnwrappableType')
_SecondUnwrappableType = TypeVar('_SecondUnwrappableType')

_ResultLikeType = TypeVar('_ResultLikeType', bound='ResultLikeN')


class ResultLikeN(
    mappable.MappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
    applicative.ApplicativeN[_FirstType, _SecondType, _ThirdType],
    altable.AltableN[_FirstType, _SecondType, _ThirdType],
    rescuable.RescuableN[_FirstType, _SecondType, _ThirdType],
):
    """
    An interface that represents a pure computation result.

    For impure result see
    :class:`returns.interfaces.specific.ioresult.IOResultLikeN` type.
    """

    @abstractmethod
    def swap(
        self: _ResultLikeType,
    ) -> KindN[_ResultLikeType, _SecondType, _FirstType, _ThirdType]:
        """Swaps value and error types in ``Result``."""

    @abstractmethod
    def bind_result(
        self: _ResultLikeType,
        function: Callable[[_FirstType], 'Result[_UpdatedType, _SecondType]'],
    ) -> KindN[_ResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Runs ``Result`` returning function over a container."""

    @classmethod
    @abstractmethod
    def from_result(
        cls: Type[_ResultLikeType],  # noqa: N805
        inner_value: 'Result[_FirstType, _SecondType]',
    ) -> KindN[_ResultLikeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""

    @classmethod
    @abstractmethod
    def from_failure(
        cls: Type[_ResultLikeType],  # noqa: N805
        inner_value: _SecondType,
    ) -> KindN[_ResultLikeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with two type arguments.
ResultLike2 = ResultLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultLike3 = ResultLikeN[_FirstType, _SecondType, _ThirdType]


class UnwrappableResult(
    ResultLikeN[_FirstType, _SecondType, _ThirdType],
    unwrappable.Unwrappable[_FirstUnwrappableType, _SecondUnwrappableType],
):
    ...


class ResultBasedN(
    UnwrappableResult[
        _FirstType,
        _SecondType,
        _ThirdType,
        # Unwraps:
        _FirstType,
        _SecondType,
    ],
):
    ...


#: Type alias for kinds with two type arguments.
ResultBased2 = ResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultBased3 = ResultBasedN[_FirstType, _SecondType, _ThirdType]
