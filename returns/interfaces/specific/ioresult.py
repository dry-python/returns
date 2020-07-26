from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, NoReturn, Type, TypeVar

from returns.interfaces.specific import io, result
from returns.interfaces import unwrappable
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.io import IO, IOResult  # noqa: WPS433
    from returns.result import Result  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOResultLikeType = TypeVar('_IOResultLikeType', bound='IOResultLikeN')


class IOResultLikeN(
    io.IOBasedN[_FirstType, _SecondType, _ThirdType],
    result.ResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    """
    An interface for types that do ``IO`` and can fail.

    It is a base interface for both sync and async ``IO`` stacks.
    """

    @abstractmethod
    def bind_ioresult(
        self: _IOResultLikeType,
        function: Callable[[_FirstType], 'IOResult[_UpdatedType, _SecondType]'],
    ) -> KindN[_IOResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Runs ``IOResult`` returning function over a container."""

    @abstractmethod
    def compose_result(
        self: _IOResultLikeType,
        function: Callable[
            ['Result[_FirstType, _SecondType]'],
            KindN[_IOResultLikeType, _UpdatedType, _SecondType, _ThirdType],
        ],
    ) -> KindN[_IOResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to compose the unrelying ``Result`` with a function."""

    @classmethod
    @abstractmethod
    def from_ioresult(
        cls: Type[_IOResultLikeType],  # noqa: N805
        inner_value: 'IOResult[_FirstType, _SecondType]',
    ) -> KindN[_IOResultLikeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from ``IOResult`` type."""

    @classmethod
    @abstractmethod
    def from_failed_io(
        cls: Type[_IOResultLikeType],  # noqa: N805
        inner_value: 'IO[_SecondType]',
    ) -> KindN[_IOResultLikeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from failed ``IO``."""


#: Type alias for kinds with two type arguments.
IOResultLike2 = IOResultLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
IOResultLike3 = IOResultLikeN[_FirstType, _SecondType, _ThirdType]


class IOResultBasedN(
    IOResultLikeN[_FirstType, _SecondType, _ThirdType],
    result.UnwrappableResult[
        _FirstType,
        _SecondType,
        _ThirdType,
        'IO[_FirstType]',
        'IO[_SecondType]',
    ],
):
    ...


#: Type alias for kinds with two type arguments.
IOResultBased2 = IOResultBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
IOResultBased3 = IOResultBasedN[_FirstType, _SecondType, _ThirdType]
