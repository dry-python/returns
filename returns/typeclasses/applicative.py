from abc import abstractmethod
from typing import Callable, Generic, Type, TypeVar

from returns.hkt import Kind

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ApplicativeType = TypeVar('_ApplicativeType', bound='Applicative')


class Applicative(Generic[_ValueType]):
    """Applicative typeclass definition."""

    @abstractmethod
    def apply(
        self: _ApplicativeType,
        container: Kind[
            _ApplicativeType,
            Callable[[_ValueType], _NewValueType],
        ],
    ) -> Kind[_ApplicativeType, _NewValueType]:
        """Allows to apply a wrapped function over a container."""

    @classmethod
    @abstractmethod
    def from_value(
        cls: Type[_ApplicativeType],  # noqa: N805
        inner_value: _NewValueType,
    ) -> Kind[_ApplicativeType, _NewValueType]:
        """Unit method to create new containers from a raw value."""
