from abc import abstractmethod
from typing import Callable, Generic, TypeVar

from returns.hkt import Kind

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_FunctorType = TypeVar('_FunctorType', bound='Functor')


class Functor(Generic[_ValueType]):
    """Functor typeclass definition."""

    @abstractmethod  # noqa: WPS125
    def map(  # noqa: WPS125
        self: _FunctorType,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Kind[_FunctorType, _NewValueType]:
        """Allows to run a pure function over a container."""
