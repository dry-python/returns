from typing import Callable, ClassVar, NoReturn, Sequence, TypeVar

from typing_extensions import final

from returns.interfaces import bindable, iterable
from returns.interfaces.applicative_mappable import ApplicativeMappableN
from returns.primitives.asserts import assert_equal
from returns.primitives.hkt import KindN
from returns.primitives.laws import Law, Law1, Law3, Lawful, LawSpecDef

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

# Only used in laws:
_NewType1 = TypeVar('_NewType1')
_NewType2 = TypeVar('_NewType2')


@final
class _LawSpec(LawSpecDef):
    """
    Container laws.

    Definition: https://wiki.haskell.org/Monad_laws
    Good explanation: https://bit.ly/2Qsi5re
    """

    @staticmethod
    def left_identity(
        raw_value: _FirstType,
        container: 'ContainerN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[
            [_FirstType],
            KindN['ContainerN', _NewType1, _SecondType, _ThirdType],
        ],
    ) -> None:
        """
        Left identity.

        The first law states that if we take a value, put it in a default
        context with return and then feed it to a function by using ``bind``,
        it's the same as just taking the value and applying the function to it.
        """
        assert_equal(
            container.from_value(raw_value).bind(function),
            function(raw_value),
        )

    @staticmethod
    def right_identity(
        container: 'ContainerN[_FirstType, _SecondType, _ThirdType]',
    ) -> None:
        """
        Right identity.

        The second law states that if we have a container value
        and we use ``bind`` to feed it to ``.from_value``,
        the result is our original container value.
        """
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
            KindN['ContainerN', _NewType1, _SecondType, _ThirdType],
        ],
        second: Callable[
            [_NewType1],
            KindN['ContainerN', _NewType2, _SecondType, _ThirdType],
        ],
    ) -> None:
        """
        Associativity law.

        The final monad law says that when
        we have a chain of container functions applications with ``bind``,
        it shouldn’t matter how they’re nested.
        """
        assert_equal(
            container.bind(first).bind(second),
            container.bind(lambda inner: first(inner).bind(second)),
        )


class ContainerN(
    ApplicativeMappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
    iterable.IterableN[_FirstType, _SecondType, _ThirdType],
    Lawful['ContainerN'],
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
