from abc import abstractmethod
from typing import ClassVar, NoReturn, Sequence, TypeVar

from typing_extensions import final

from returns.interfaces import bimappable
from returns.primitives.asserts import assert_equal
from returns.primitives.hkt import KindN
from returns.primitives.laws import (
    Law,
    Law1,
    Lawful,
    LawSpecDef,
    law_definition,
)

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_SwappableType = TypeVar('_SwappableType', bound='SwappableN')


@final
class _LawSpec(LawSpecDef):
    """Laws for :class:`~SwappableN` type."""

    @law_definition
    def double_swap_law(
        container: 'SwappableN[_FirstType, _SecondType, _ThirdType]',
    ) -> None:
        """
        Swaaping container twice.

        It ensure that we get the initial value back.
        In other words, swapping twice does nothing.
        """
        assert_equal(
            container,
            container.swap().swap(),
        )


class SwappableN(
    bimappable.BiMappableN[_FirstType, _SecondType, _ThirdType],
    Lawful['SwappableN[_FirstType, _SecondType, _ThirdType]'],
):
    """Interface that allows swapping first and second type values."""

    _laws: ClassVar[Sequence[Law]] = (
        Law1(_LawSpec.double_swap_law),
    )

    @abstractmethod
    def swap(
        self: _SwappableType,
    ) -> KindN[_SwappableType, _SecondType, _FirstType, _ThirdType]:
        """Swaps first and second types in ``SwappableN``."""


#: Type alias for kinds with two type arguments.
Swappable2 = SwappableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Swappable3 = SwappableN[_FirstType, _SecondType, _ThirdType]
