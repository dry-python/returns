from typing import Generic, ClassVar, Sequence, TypeVar, Callable
from itertools import chain

from typing_extensions import final

_Caps = TypeVar('_Caps')
_ReturnType = TypeVar('_ReturnType')
_TypeArgType1 = TypeVar('_TypeArgType1')
_TypeArgType2 = TypeVar('_TypeArgType2')
_TypeArgType3 = TypeVar('_TypeArgType3')


class Law(object):
    @property
    def name(self) -> str:
        return self._function.__name__  # type: ignore


class Law1(
    Law,
    Generic[_TypeArgType1, _ReturnType],
):
    def __init__(
        self,
        function: Callable[[_TypeArgType1], _ReturnType],
    ) -> None:
        self._function = function

    def run(
        self,
        arg1: _TypeArgType1,
    ) -> _ReturnType:
        return self._function(arg1)


class Law2(
    Law,
    Generic[_TypeArgType1, _TypeArgType2, _ReturnType],
):
    def __init__(
        self,
        function: Callable[[_TypeArgType1, _TypeArgType2], _ReturnType],
    ) -> None:
        self._function = function

    def run(
        self,
        arg1: _TypeArgType1,
        arg2: _TypeArgType2,
    ) -> _ReturnType:
        return self._function(arg1, arg2)


class Law3(
    Law,
    Generic[_TypeArgType1, _TypeArgType2, _TypeArgType3, _ReturnType],
):
    def __init__(
        self,
        function: Callable[
            [_TypeArgType1, _TypeArgType2, _TypeArgType3],
            _ReturnType,
        ],
    ) -> None:
        self._function = function

    def run(
        self,
        arg1: _TypeArgType1,
        arg2: _TypeArgType2,
        arg3: _TypeArgType3,
    ) -> _ReturnType:
        return self._function(arg1, arg2, arg3)


class Lawful(Generic[_Caps]):
    _laws: ClassVar[Sequence[Law]]

    @final
    @classmethod
    def laws(cls) -> Sequence[Law]:
        return tuple(chain.from_iterable(
            getattr(klass, '_laws', ())
            for klass in cls.__mro__
        ))
