from itertools import chain
from typing import Callable, ClassVar, Generic, Sequence, TypeVar

from typing_extensions import final

from returns.primitives.types import Immutable

_Caps = TypeVar('_Caps')
_ReturnType = TypeVar('_ReturnType')
_TypeArgType1 = TypeVar('_TypeArgType1')
_TypeArgType2 = TypeVar('_TypeArgType2')
_TypeArgType3 = TypeVar('_TypeArgType3')


class Law(Immutable):
    """Base class for all laws. Does not have an attached signature."""

    __slots__ = ('definition', )
    definition: Callable

    @final
    @property
    def name(self) -> str:
        return self.definition.__name__


@final
class Law1(
    Law,
    Generic[_TypeArgType1, _ReturnType],
):
    """Law definition for functions with a single argument."""

    definition: Callable[['Law1', _TypeArgType1], _ReturnType]

    def __init__(
        self,
        function: Callable[[_TypeArgType1], _ReturnType],
    ) -> None:
        object.__setattr__(self, 'definition', function)


@final
class Law2(
    Law,
    Generic[_TypeArgType1, _TypeArgType2, _ReturnType],
):
    """Law definition for functions with two arguments."""

    definition: Callable[['Law2', _TypeArgType1, _TypeArgType2], _ReturnType]

    def __init__(
        self,
        function: Callable[[_TypeArgType1, _TypeArgType2], _ReturnType],
    ) -> None:
        object.__setattr__(self, 'definition', function)


@final
class Law3(
    Law,
    Generic[_TypeArgType1, _TypeArgType2, _TypeArgType3, _ReturnType],
):
    """Law definition for functions with three argument."""

    definition: Callable[
        ['Law3', _TypeArgType1, _TypeArgType2, _TypeArgType3],
        _ReturnType,
    ]

    def __init__(
        self,
        function: Callable[
            [_TypeArgType1, _TypeArgType2, _TypeArgType3],
            _ReturnType,
        ],
    ) -> None:
        object.__setattr__(self, 'definition', function)


class Lawful(Generic[_Caps]):
    """
    Base class for all lawful classes.

    Allows to smartly collect all defined laws from all parent classes.
    """

    #: Some classes and interfaces might have laws, some might not have any.
    _laws: ClassVar[Sequence[Law]]

    @final
    @classmethod
    def laws(cls) -> Sequence[Law]:
        """
        Collects all laws from all parent classes.

        Algorithm:
        1. First, we collect all unique parents in ``__mro__`
        2. Then we get the laws definition from each of them
        3. Then we flatten the result iterable

        """
        seen = {}
        for parent in cls.__mro__:
            if parent.__qualname__ not in seen:
                seen[parent.__qualname__] = parent
        return tuple(chain.from_iterable(
            # We use __dict__ here because we don't want to triger
            # attribute access, which can resolve laws from parent classes.
            klass.__dict__.get('_laws', ())
            for klass in seen.values()
        ))


class LawSpecDef(object):
    """Base class for all collection of laws aka LawSpecs."""

    __slots__ = ()
