from abc import abstractmethod
from typing import Callable, ClassVar, Generic, NoReturn, Sequence, TypeVar

from returns.functions import compose, identity
from returns.primitives.asserts import assert_equal
from returns.primitives.hkt import KindN
from returns.primitives.laws import Law, Law1, Law2, Law3, Lawful, LawSpecDef

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_MappableType = TypeVar('_MappableType', bound='MappableN')

# Used in laws:
_NewType1 = TypeVar('_NewType1')
_NewType2 = TypeVar('_NewType2')


class _LawSpec(LawSpecDef):

    @staticmethod
    def identity_law(
        mappable: 'MappableN[_FirstType, _SecondType, _ThirdType]',
    ) -> None:
        assert_equal(mappable.map(identity), mappable)

    @staticmethod
    def associativity_law(
        mappable: 'MappableN[_FirstType, _SecondType, _ThirdType]',
        first: Callable[[_FirstType], _NewType1],
        second: Callable[[_NewType1], _NewType2],
    ) -> None:
        assert_equal(
            mappable.map(first).map(second),
            mappable.map(compose(first, second)),
        )


class MappableN(
    Generic[_FirstType, _SecondType, _ThirdType],
    Lawful['MappableN'],
):
    """
    Allows to chain wrapped values in containers with regular functions.

    Behaves like a functor.

    See also:
        https://en.wikipedia.org/wiki/Functor
    """

    _laws: ClassVar[Sequence[Law]] = (
        Law1(_LawSpec.identity_law),
        Law3(_LawSpec.associativity_law),
    )

    @abstractmethod  # noqa: WPS125
    def map(  # noqa: WPS125
        self: _MappableType,
        function: Callable[[_FirstType], _UpdatedType],
    ) -> KindN[_MappableType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to run a pure function over a container."""


#: Type alias for kinds with one type argument.
Mappable1 = MappableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Mappable2 = MappableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Mappable3 = MappableN[_FirstType, _SecondType, _ThirdType]
