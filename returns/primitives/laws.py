from itertools import chain
from typing import Callable, ClassVar, Dict, Generic, Sequence, Type, TypeVar

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
    def laws(cls) -> Dict[Type['Lawful'], Sequence[Law]]:
        """
        Collects all laws from all parent classes.

        Algorithm:
        1. First, we collect all unique parents in ``__mro__`
        2. Then we get the laws definition from each of them
        3. Then we structure them in a ``type: its_laws`` way

        """
        seen = {}
        for parent in cls.__mro__:
            fullname = '{0}.{1}'.format(parent.__module__, parent.__qualname__)
            if fullname not in seen:
                seen[fullname] = parent

        laws = {}
        for klass in seen.values():
            current_laws = klass.__dict__.get('_laws', ())
            if not current_laws:
                continue
            laws[klass] = current_laws
        return laws


class LawSpecDef(object):
    """Base class for all collection of laws aka LawSpecs."""

    __slots__ = ()
