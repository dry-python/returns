from abc import abstractmethod
from typing import Callable, Generic, TypeVar

from returns.hkt import Kind

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_MonadType = TypeVar('_MonadType', bound='Monad')


class Monad(Generic[_ValueType]):  # TODO: change naming later
    """Monad typeclass definition."""

    @abstractmethod  # noqa: WPS125
    def bind(  # noqa: WPS125
        self: _MonadType,
        function: Callable[[_ValueType], Kind[_MonadType, _NewValueType]],
    ) -> Kind[_MonadType, _NewValueType]:
        """Allows to run a function returning a container over a container."""
