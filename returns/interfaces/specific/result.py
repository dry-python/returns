from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, NoReturn, Type, TypeVar

from returns.interfaces import (
    altable,
    applicative,
    bindable,
    mappable,
    rescuable,
)
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ResultBasedType = TypeVar('_ResultBasedType', bound='ResultBasedN')


class ResultBasedN(
    mappable.MappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
    applicative.ApplicativeN[_FirstType, _SecondType, _ThirdType],
    altable.AltableN[_FirstType, _SecondType, _ThirdType],
    rescuable.RescuableN[_FirstType, _SecondType, _ThirdType],
):
    """
    An interface that represents a pure computation result.

    For impure result see
    :class:`returns.interfaces.specific.ioresult.IOResultBasedN` type.
    """

    @abstractmethod
    def swap(
        self: _ResultBasedType,
    ) -> KindN[_ResultBasedType, _SecondType, _FirstType, _ThirdType]:
        """Swaps value and error types in ``Result``."""

    @abstractmethod
    def bind_result(
        self: _ResultBasedType,
        function: Callable[[_FirstType], 'Result[_UpdatedType, _SecondType]'],
    ) -> KindN[_ResultBasedType, _UpdatedType, _SecondType, _ThirdType]:
        """Runs ``Result`` returning function over a container."""

    @classmethod
    @abstractmethod
    def from_result(
        cls: Type[_ResultBasedType],  # noqa: N805
        inner_value: 'Result[_FirstType, _SecondType]',
    ) -> KindN[_ResultBasedType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""

    @classmethod
    @abstractmethod
    def from_failure(
        cls: Type[_ResultBasedType],  # noqa: N805
        inner_value: _SecondType,
    ) -> KindN[_ResultBasedType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with one type argument.
ResultBased1 = ResultBasedN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
ResultBased2 = ResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultBased3 = ResultBasedN[_FirstType, _SecondType, _ThirdType]
