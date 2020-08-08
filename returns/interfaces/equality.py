from returns.primitives.laws import Lawful, Law1, Law2, Law3
from typing import TypeVar
from abc import abstractmethod

_EqualType = TypeVar('_EqualType', bound='SupportsEquality')


class _LawSpec(object):
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
        assert first.equals(second) is second.equals(first)

    @staticmethod
    def transitivity_law(
        first: _EqualType,
        second: _EqualType,
        third: _EqualType,
    ) -> None:
        if first.equals(second) and second.equals(third):
            assert first.equals(third)


class SupportsEquality(Lawful['SupportsEquality']):
    _laws = (
        Law1(_LawSpec.reflexive_law),
        Law2(_LawSpec.symmetry_law),
        Law3(_LawSpec.transitivity_law),
    )

    @abstractmethod
    def equals(self: _EqualType, other: _EqualType) -> bool:
        ...
