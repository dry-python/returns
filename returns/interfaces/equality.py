from abc import abstractmethod
from typing import ClassVar, Sequence, TypeVar

from returns.primitives.laws import Law, Law1, Law2, Law3, Lawful, LawSpecDef

_EqualType = TypeVar('_EqualType', bound='SupportsEquality')


class _LawSpec(LawSpecDef):
    @staticmethod
    def reflexive_law(
        first: _EqualType,
    ) -> None:
        assert first.equals(first)

    @staticmethod
    def symmetry_law(
        first: _EqualType,
        second: _EqualType,
    ) -> None:
        if first.equals(second):
            assert second.equals(first)

    @staticmethod
    def transitivity_law(
        first: _EqualType,
        second: _EqualType,
        third: _EqualType,
    ) -> None:
        if first.equals(second) and second.equals(third):
            assert first.equals(third)


class SupportsEquality(Lawful['SupportsEquality']):
    _laws: ClassVar[Sequence[Law]] = (
        Law1(_LawSpec.reflexive_law),
        Law2(_LawSpec.symmetry_law),
        Law3(_LawSpec.transitivity_law),
    )

    @abstractmethod
    def equals(self: _EqualType, other: _EqualType) -> bool:
        ...
