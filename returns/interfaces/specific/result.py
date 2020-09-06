"""
An interface that represents a pure computation result.

For impure result see
:class:`returns.interfaces.specific.ioresult.IOResultLikeN` type.
"""

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    NoReturn,
    Sequence,
    Type,
    TypeVar,
)

from typing_extensions import final

from returns.interfaces import bimappable, equable, rescuable, unwrappable
from returns.interfaces.container import ContainerN
from returns.primitives.asserts import assert_equal
from returns.primitives.hkt import KindN
from returns.primitives.laws import (
    Law,
    Law3,
    Lawful,
    LawSpecDef,
    law_definition,
)

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ResultLikeType = TypeVar('_ResultLikeType', bound='ResultLikeN')

# New values:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Unwrappable:
_FirstUnwrappableType = TypeVar('_FirstUnwrappableType')
_SecondUnwrappableType = TypeVar('_SecondUnwrappableType')

# Used in laws:
_NewType1 = TypeVar('_NewType1')


@final
class _LawSpec(LawSpecDef):
    """
    Result laws.

    We need to be sure that ``.map``, ``.bind``, ``.alt``, and ``.rescue``
    works correctly for both success and failure types.
    """

    @law_definition
    def map_short_circuit_law(
        raw_value: _SecondType,
        container: 'ResultLikeN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[[_FirstType], _NewType1],
    ) -> None:
        """Ensures that you cannot map a failure."""
        assert_equal(
            container.from_failure(raw_value),
            container.from_failure(raw_value).map(function),
        )

    @law_definition
    def bind_short_circuit_law(
        raw_value: _SecondType,
        container: 'ResultLikeN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[
            [_FirstType],
            KindN['ResultLikeN', _NewType1, _SecondType, _ThirdType],
        ],
    ) -> None:
        """
        Ensures that you cannot bind a failure.

        See: https://wiki.haskell.org/Typeclassopedia#MonadFail
        """
        assert_equal(
            container.from_failure(raw_value),
            container.from_failure(raw_value).bind(function),
        )

    @law_definition
    def alt_short_circuit_law(
        raw_value: _SecondType,
        container: 'ResultLikeN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[[_SecondType], _NewType1],
    ) -> None:
        """Ensures that you cannot alt a success."""
        assert_equal(
            container.from_value(raw_value),
            container.from_value(raw_value).alt(function),
        )

    @law_definition
    def rescue_short_circuit_law(
        raw_value: _FirstType,
        container: 'ResultLikeN[_FirstType, _SecondType, _ThirdType]',
        function: Callable[
            [_SecondType],
            KindN['ResultLikeN', _FirstType, _NewType1, _ThirdType],
        ],
    ) -> None:
        """Ensures that you cannot rescue a success."""
        assert_equal(
            container.from_value(raw_value),
            container.from_value(raw_value).rescue(function),
        )


class ResultLikeN(
    ContainerN[_FirstType, _SecondType, _ThirdType],
    bimappable.BiMappableN[_FirstType, _SecondType, _ThirdType],
    rescuable.RescuableN[_FirstType, _SecondType, _ThirdType],
    Lawful['ResultLikeN[_FirstType, _SecondType, _ThirdType]'],
):
    """
    Base types for types that looks like ``Result`` but cannot be unwrapped.

    Like ``RequiresContextResult`` or ``FutureResult``.
    """

    _laws: ClassVar[Sequence[Law]] = (
        Law3(_LawSpec.map_short_circuit_law),
        Law3(_LawSpec.bind_short_circuit_law),
        Law3(_LawSpec.alt_short_circuit_law),
        Law3(_LawSpec.rescue_short_circuit_law),
    )

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
        inner_value: 'Result[_ValueType, _ErrorType]',
    ) -> KindN[_ResultLikeType, _ValueType, _ErrorType, _ThirdType]:
        """Unit method to create new containers from any raw value."""

    @classmethod
    @abstractmethod
    def from_failure(
        cls: Type[_ResultLikeType],  # noqa: N805
        inner_value: _ErrorType,
    ) -> KindN[_ResultLikeType, _FirstType, _ErrorType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with two type arguments.
ResultLike2 = ResultLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultLike3 = ResultLikeN[_FirstType, _SecondType, _ThirdType]


class UnwrappableResult(
    ResultLikeN[_FirstType, _SecondType, _ThirdType],
    unwrappable.Unwrappable[_FirstUnwrappableType, _SecondUnwrappableType],
    equable.SupportsEquality,
):
    """
    Intermediate type with 5 type arguments that represents unwrappable result.

    It is a raw type and should not be used directly.
    Use ``ResultBasedN`` and ``IOResultBasedN`` instead.
    """


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
    """
    Base type for real ``Result`` types.

    Can be unwrapped.
    """


#: Type alias for kinds with two type arguments.
ResultBased2 = ResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
ResultBased3 = ResultBasedN[_FirstType, _SecondType, _ThirdType]
