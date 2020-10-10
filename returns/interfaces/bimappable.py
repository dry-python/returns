from abc import abstractmethod
from typing import ClassVar, NoReturn, Sequence, TypeVar

from typing_extensions import final

from returns.interfaces import altable, mappable
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

_BiMappableType = TypeVar('_BiMappableType', bound='BiMappableN')


@final
class _LawSpec(LawSpecDef):
    """Laws for :class:`~BiMappableN` type."""

    @law_definition
    def double_swap_law(
        container: 'BiMappableN[_FirstType, _SecondType, _ThirdType]',
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


class BiMappableN(
    mappable.MappableN[_FirstType, _SecondType, _ThirdType],
    altable.AltableN[_FirstType, _SecondType, _ThirdType],
    Lawful['BiMappableN[_FirstType, _SecondType, _ThirdType]'],
):
    """
    Allows to change both types of a container at the same time.

    Uses ``.map`` to change first type and ``.alt`` to change second type.

    See also:
        - https://typelevel.org/cats/typeclasses/bifunctor.html

    """

    _laws: ClassVar[Sequence[Law]] = (
        Law1(_LawSpec.double_swap_law),
    )

    @abstractmethod
    def swap(
        self: _BiMappableType,
    ) -> KindN[_BiMappableType, _SecondType, _FirstType, _ThirdType]:
        """Swaps first and second types in ``BiMappableN``."""


#: Type alias for kinds with two type arguments.
BiMappable2 = BiMappableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
BiMappable3 = BiMappableN[_FirstType, _SecondType, _ThirdType]
