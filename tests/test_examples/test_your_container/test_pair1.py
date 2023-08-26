from typing import Callable, Tuple, TypeVar, final

from returns.interfaces import bindable, equable, lashable, swappable
from returns.primitives.container import BaseContainer, container_equality
from returns.primitives.hkt import Kind2, SupportsKind2, dekind

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')

_NewFirstType = TypeVar('_NewFirstType')
_NewSecondType = TypeVar('_NewSecondType')


@final
class Pair(
    BaseContainer,
    SupportsKind2['Pair', _FirstType, _SecondType],
    bindable.Bindable2[_FirstType, _SecondType],
    swappable.Swappable2[_FirstType, _SecondType],
    lashable.Lashable2[_FirstType, _SecondType],
    equable.Equable,
):
    """
    A type that represents a pair of something.

    Like to coordinates ``(x, y)`` or two best friends.
    Or a question and an answer.

    """

    def __init__(
        self,
        inner_value: Tuple[_FirstType, _SecondType],
    ) -> None:
        """Saves passed tuple as ``._inner_value`` inside this instance."""
        super().__init__(inner_value)

    # `Equable` part:

    equals = container_equality  # we already have this defined for all types

    # `Mappable` part via `BiMappable`:

    def map(
        self,
        function: Callable[[_FirstType], _NewFirstType],
    ) -> 'Pair[_NewFirstType, _SecondType]':
        return Pair((function(self._inner_value[0]), self._inner_value[1]))

    # `BindableN` part:

    def bind(
        self,
        function: Callable[
            [_FirstType],
            Kind2['Pair', _NewFirstType, _SecondType],
        ],
    ) -> 'Pair[_NewFirstType, _SecondType]':
        return dekind(function(self._inner_value[0]))

    # `AltableN` part via `BiMappableN`:

    def alt(
        self,
        function: Callable[[_SecondType], _NewSecondType],
    ) -> 'Pair[_FirstType, _NewSecondType]':
        return Pair((self._inner_value[0], function(self._inner_value[1])))

    # `LashableN` part:

    def lash(
        self,
        function: Callable[
            [_SecondType],
            Kind2['Pair', _FirstType, _NewSecondType],
        ],
    ) -> 'Pair[_FirstType, _NewSecondType]':
        return dekind(function(self._inner_value[1]))

    # `SwappableN` part:

    def swap(self) -> 'Pair[_SecondType, _FirstType]':
        return Pair((self._inner_value[1], self._inner_value[0]))
