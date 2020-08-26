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
    _laws: ClassVar[Sequence[Law]]

    @final
    @classmethod
    def laws(cls) -> Sequence[Law]:
        seen = {}
        for parent in cls.__mro__:
            if parent.__qualname__ not in seen:
                seen[parent.__qualname__] = parent
        return tuple(chain.from_iterable(
            klass.__dict__.get('_laws', ())
            for klass in seen.values()
        ))


class LawSpecDef(object):
    __slots__ = ()
