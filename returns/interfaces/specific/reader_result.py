from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Type, TypeVar

from returns.interfaces.specific import reader, result
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.context import Reader, ReaderResult  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_EnvType = TypeVar('_EnvType')

_ReaderResultLikeType = TypeVar(
    '_ReaderResultLikeType',
    bound='ReaderResultLikeN',
)


class ReaderResultLikeN(
    reader.ReaderLike3[_FirstType, _SecondType, _ThirdType],
    result.ResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    """
    Base interface for all types that do look like ``ReaderResult`` instance.

    Cannot be called.
    """

    @abstractmethod
    def bind_context_result(
        self: _ReaderResultLikeType,
        function: Callable[
            [_FirstType],
            'ReaderResult[_UpdatedType, _SecondType, _ThirdType]',
        ],
    ) -> KindN[_ReaderResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Binds a ``ReaderResult`` returning function over a container."""

    @classmethod
    @abstractmethod
    def from_failed_context(
        cls: Type[_ReaderResultLikeType],  # noqa: N805
        inner_value: 'Reader[_ErrorType, _EnvType]',
    ) -> KindN[_ReaderResultLikeType, _FirstType, _ErrorType, _EnvType]:
        """Unit method to create new containers from failed ``Reader``."""


class ReaderResultBasedN(
    ReaderResultLikeN[_FirstType, _SecondType, _ThirdType],
    reader.CallableReader3[
        _FirstType,
        _SecondType,
        _ThirdType,
        # Calls:
        'Result[_FirstType, _SecondType]',
        _ThirdType,
    ],
):
    """
    This interface is very specific to our ``ReaderResult`` type.

    The only thing that differs from ``ReaderResultLikeN`` is that we know
    the specific types for its ``__call__`` method.

    In this case the return type of ``__call__`` is ``Result``.
    """
