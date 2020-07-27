from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, NoReturn, Type, TypeVar

from returns.interfaces.aliases import container
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.io import IO  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOBasedType = TypeVar('_IOBasedType', bound='IOBasedN')


class IOBasedN(container.ContainerN[_FirstType, _SecondType, _ThirdType]):
    """
    Represents the base interfaces for types that do fearless ``IO``.

    This type means that ``IO`` cannot fail. Like random numbers, date, etc.
    Don't use this type for ``IO`` that can. Instead, use
    :class:`returns.interfaces.specific.ioresult.IOResultBasedN` type.

    """

    @abstractmethod
    def bind_io(
        self: _IOBasedType,
        function: Callable[[_FirstType], 'IO[_UpdatedType]'],
    ) -> KindN[_IOBasedType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a container."""

    @classmethod
    @abstractmethod
    def from_io(
        cls: Type[_IOBasedType],  # noqa: N805
        inner_value: 'IO[_FirstType]',
    ) -> KindN[_IOBasedType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from successful ``IO``."""


#: Type alias for kinds with one type argument.
IOBased1 = IOBasedN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
IOBased2 = IOBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
IOBased3 = IOBasedN[_FirstType, _SecondType, _ThirdType]
