import sys
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    TypedDict,
    TypeVar,
)

# Use typing_extensions for Self if Python < 3.11 OR if just type checking
# (safer for Mypy compatibility across different check versions)
if sys.version_info >= (3, 11) and not TYPE_CHECKING:
    from typing import Self  # pragma: py-lt-311
else:
    # This branch is taken at runtime for Py < 3.11
    # AND during static analysis (TYPE_CHECKING=True)
    from typing_extensions import Self  # pragma: py-gte-311

from returns.interfaces.equable import Equable
from returns.primitives.hkt import Kind1
from returns.primitives.types import Immutable

_EqualType = TypeVar('_EqualType', bound=Equable)


class _PickleState(TypedDict):
    """Dict to represent the `BaseContainer` state to be pickled."""

    # TODO: Remove `__slots__` from here when `slotscheck` allow ignore classes
    # by using comments. We don't need the slots here since this class is just
    # a representation of a dictionary and should not be instantiated by any
    # means.
    # See: https://github.com/ariebovenberg/slotscheck/issues/71
    __slots__ = ('container_value',)  # type: ignore

    container_value: Any


class BaseContainer(Immutable, ABC):
    """
    Utility class to provide all needed magic methods to the context.

    Supports standard magic methods like ``__eq__``, ``__hash__``,
    ``__repr__``, and ``__getstate__`` / ``__setstate__`` for pickling.

    Since Python 3.13, also supports ``copy.replace()`` via the
    ``__replace__`` magic method.
    """

    __slots__ = ('_inner_value',)
    _inner_value: Any

    def __init__(self, inner_value) -> None:
        """
        Wraps the given value in the Container.

        'value' is any arbitrary value of any type including functions.
        """
        object.__setattr__(self, '_inner_value', inner_value)

    def __repr__(self) -> str:
        """Used to display details of object."""
        return '<{}: {}>'.format(
            self.__class__.__qualname__.strip('_'),
            str(self._inner_value),
        )

    def __eq__(self, other: object) -> bool:
        """Used to compare two 'Container' objects."""
        return container_equality(self, other)  # type: ignore

    def __hash__(self) -> int:
        """Used to use this value as a key."""
        return hash(self._inner_value)

    def __getstate__(self) -> _PickleState:
        """That's how this object will be pickled."""
        return {'container_value': self._inner_value}  # type: ignore

    def __setstate__(self, state: _PickleState | Any) -> None:
        """Loading state from pickled data."""
        if isinstance(state, dict) and 'container_value' in state:
            object.__setattr__(
                self,
                '_inner_value',
                state['container_value'],
            )
        else:
            # backward compatibility with 0.19.0 and earlier
            object.__setattr__(self, '_inner_value', state)

    def __replace__(self, **changes: Any) -> Self:
        """
        Custom implementation for copy.replace() (Python 3.13+).

        Creates a new instance of the container with specified changes.
        For BaseContainer and its direct subclasses, only replacing
        the '_inner_value' is generally supported via the constructor.

        Args:
            **changes: Keyword arguments mapping attribute names to new values.
                       Currently only ``_inner_value`` is supported.

        Returns:
            A new container instance with the specified replacements, or
            ``self`` if no changes were provided (due to immutability).

        Raises:
            TypeError: If 'changes' contains keys other than '_inner_value'.
        """
        # If no changes, return self (immutability principle)
        if not changes:
            return self

        # Define which attributes can be replaced in the base container logic
        allowed_keys = {'_inner_value'}
        provided_keys = set(changes.keys())

        # Check if any unexpected attributes were requested for change
        if not provided_keys.issubset(allowed_keys):
            unexpected_keys = provided_keys - allowed_keys
            raise TypeError(
                f'{type(self).__name__}.__replace__ received unexpected '
                f'arguments: {unexpected_keys}'
            )

        # Determine the inner value for the new container
        new_inner_value = changes.get(
            '_inner_value',
            self._inner_value,
        )

        # Create a new instance of the *actual* container type (e.g., Success)
        return type(self)(new_inner_value)


def container_equality(
    self: Kind1[_EqualType, Any],
    other: Kind1[_EqualType, Any],
) -> bool:
    """
    Function to compare similar containers.

    Compares both their types and their inner values.
    """
    if type(self) != type(other):  # noqa: WPS516, E721
        return False
    return bool(
        self._inner_value == other._inner_value,  # type: ignore # noqa: SLF001
    )
