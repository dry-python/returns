from abc import abstractmethod
from collections.abc import Callable, Sequence
from typing import ClassVar, Generic, TypeAlias, TypeVar, final

import pytest
from hypothesis.errors import ResolutionFailed
from typing_extensions import Never

from returns.contrib.hypothesis.laws import check_all_laws
from returns.functions import compose, identity
from returns.primitives.asserts import assert_equal
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import KindN, SupportsKind1
from returns.primitives.laws import (
    Law,
    Law1,
    Law3,
    Lawful,
    LawSpecDef,
    law_definition,
)

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_MappableType = TypeVar('_MappableType', bound='_MappableN')
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')

# Used in laws:
_NewType1 = TypeVar('_NewType1')
_NewType2 = TypeVar('_NewType2')


@final
class _LawSpec(LawSpecDef):
    """Copy of the functor laws for `MappableN`."""

    __slots__ = ()

    @law_definition
    def identity_law(
        mappable: '_MappableN[_FirstType, _SecondType, _ThirdType]',
    ) -> None:
        """Mapping identity over a value must return the value unchanged."""
        assert_equal(mappable.map(identity), mappable)

    @law_definition
    def associative_law(
        mappable: '_MappableN[_FirstType, _SecondType, _ThirdType]',
        first: Callable[[_FirstType], _NewType1],
        second: Callable[[_NewType1], _NewType2],
    ) -> None:
        """Mapping twice or mapping a composition is the same thing."""
        assert_equal(
            mappable.map(first).map(second),
            mappable.map(compose(first, second)),
        )


class _MappableN(
    Lawful['_MappableN[_FirstType, _SecondType, _ThirdType]'],
    Generic[_FirstType, _SecondType, _ThirdType],
):
    """Simple "user-defined" copy of `MappableN`."""

    __slots__ = ()

    _laws: ClassVar[Sequence[Law]] = (
        Law1(_LawSpec.identity_law),
        Law3(_LawSpec.associative_law),
    )

    @abstractmethod  # noqa: WPS125
    def map(
        self: _MappableType,
        function: Callable[[_FirstType], _UpdatedType],
    ) -> KindN[_MappableType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to run a pure function over a container."""


_Mappable1: TypeAlias = _MappableN[_FirstType, Never, Never]


class _Wrapper(
    BaseContainer,
    SupportsKind1['_Wrapper', _ValueType],
    _Mappable1[_ValueType],
):
    """Simple instance of `_MappableN`."""

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        super().__init__(inner_value)

    def map(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> '_Wrapper[_NewValueType]':
        return _Wrapper(function(self._inner_value))


pytestmark = pytest.mark.xfail(raises=ResolutionFailed)

check_all_laws(_Wrapper)
