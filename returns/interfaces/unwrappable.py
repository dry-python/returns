from abc import abstractmethod
from typing import Generic, TypeVar

_FirstType_co = TypeVar('_FirstType_co', covariant=True)
_SecondType_co = TypeVar('_SecondType_co', covariant=True)

_UnwrappableType = TypeVar('_UnwrappableType', bound='Unwrappable')


class Unwrappable(Generic[_FirstType_co, _SecondType_co]):
    """
    Represents containers that can unwrap and return its wrapped value.

    There are no aliases or ``UnwrappableN`` for ``Unwrappable`` interface.
    Because it always uses two and just two types.

    Not all types can be ``Unwrappable`` because we do require
    to raise ``UnwrapFailedError`` if unwrap is not possible.
    """

    __slots__ = ()

    @abstractmethod
    def unwrap(self: _UnwrappableType) -> _FirstType_co:
        """
        Custom magic method to unwrap inner value from container.

        Should be redefined for ones that actually have values.
        And for ones that raise an exception for no values.

        .. note::
            As a part of the contract, failed ``unwrap`` calls
            must raise :class:`returns.primitives.exceptions.UnwrapFailedError`
            exception.

        This method is the opposite of :meth:`~Unwrapable.failure`.
        """

    @abstractmethod
    def failure(self: _UnwrappableType) -> _SecondType_co:
        """
        Custom magic method to unwrap inner value from the failed container.

        .. note::
            As a part of the contract, failed ``failure`` calls
            must raise :class:`returns.primitives.exceptions.UnwrapFailedError`
            exception.

        This method is the opposite of :meth:`~Unwrapable.unwrap`.
        """
