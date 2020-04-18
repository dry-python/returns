from abc import ABCMeta
from typing import Any, TypeVar

from returns.primitives.types import Immutable

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')


class BaseContainer(Immutable, metaclass=ABCMeta):
    """Utility class to provide all needed magic methods to the context."""

    __slots__ = ('_inner_value',)
    _inner_value: Any

    def __init__(self, inner_value) -> None:
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)  # noqa: WPS609

    def __str__(self) -> str:
        """Converts to string."""
        return '<{0}: {1}>'.format(
            self.__class__.__qualname__.strip('_'),
            str(self._inner_value),
        )

    def __eq__(self, other: Any) -> bool:
        """Used to compare two 'Container' objects."""
        if not isinstance(self, type(other)):
            return False
        return self._inner_value == other._inner_value  # noqa: WPS437

    def __hash__(self) -> int:
        """Used to use this value as a key."""
        return hash(self._inner_value)

    def __getstate__(self) -> Any:
        """That's how this object will be pickled."""
        return self._inner_value

    def __setstate__(self, state: Any) -> None:
        """Loading state from pickled data."""
        object.__setattr__(self, '_inner_value', state)  # noqa: WPS609
