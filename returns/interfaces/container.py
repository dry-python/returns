from typing import NoReturn, TypeVar, ClassVar, Sequence, Any, Type, Callable

from typing_extensions import final

from returns.interfaces import bindable, iterable
from returns.interfaces.applicative_mappable import ApplicativeMappableN
from returns.primitives.laws import LawSpecDef, Lawful, Law, Law1, Law2, Law3
from returns.primitives.asserts import assert_equal

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

# Only used in laws:
_NewType1 = TypeVar('_NewType1')
_NewType2 = TypeVar('_NewType2')


@final
class _LawSpec(LawSpecDef):
    """
    Bindable laws.

    https://wiki.haskell.org/Monad_laws
    """

    @staticmethod
    def left_identity(
        raw_value: _FirstType,
        container: 'ContainerN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[
            [_FirstType],
            'ContainerN[_FirstType, _SecondType, _ThirdType]',
        ],
    ) -> None:
        """TODO."""
        assert_equal(
            container.from_value(raw_value).bind(function),
            function(raw_value),
        )

    @staticmethod
    def right_identity(
        container: 'ContainerN[_FirstType, _SecondType, _ThirdType]',
    ) -> None:
        """TODO."""
        assert_equal(
            container,
            container.bind(
                lambda inner: container.from_value(inner),
            ),
        )

    @staticmethod
    def associativity(
        container: 'ContainerN[_FirstType, _SecondType, _ThirdType]',
        first: Callable[
            [_FirstType],
            'ContainerN[_NewType1, _SecondType, _ThirdType]',
        ],
        second: Callable[
            [_FirstType],
            'ContainerN[_NewType2, _SecondType, _ThirdType]',
        ],
    ) -> None:
        """TODO"""
        assert_equal(
            container.bind(first).bind(second),
            container.bind(lambda inner: first(inner).bind(second)),
        )


class ContainerN(
    ApplicativeMappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
    iterable.IterableN[_FirstType, _SecondType, _ThirdType],
):
    """
    Handy alias for types with ``.bind``, ``.map``, and ``.apply`` methods.

    Should be a base class for almost any containers you write.

    See also:
        https://bit.ly/2CTEVov

    """

    _laws: ClassVar[Sequence[Law]] = (
        Law3(_LawSpec.left_identity),
        Law1(_LawSpec.right_identity),
        Law3(_LawSpec.associativity),
    )


#: Type alias for kinds with one type argument.
Container1 = ContainerN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Container2 = ContainerN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Container3 = ContainerN[_FirstType, _SecondType, _ThirdType]
