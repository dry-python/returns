from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Type, TypeVar

from returns.interfaces.specific import result, reader
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.result import Result  # noqa: WPS433
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
    result.ResultLikeN[_FirstType, _SecondType, _ThirdType],
    reader.ReaderLike3[_FirstType, _SecondType, _ThirdType],
):
    @abstractmethod
    def bind_context_result(
        self: _ReaderResultLikeType,
        function: Callable[
            [_FirstType],
            'ReaderResult[_UpdatedType, _SecondType, _ThirdType]',
        ],
    ) -> KindN[_ReaderResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        ...

    @classmethod
    @abstractmethod
    def from_failed_context(
        cls: Type[_ReaderResultLikeType],  # noqa: N805
        inner_value: 'Reader[_ErrorType, _EnvType]',
    ) -> KindN[_ReaderResultLikeType, _FirstType, _ErrorType, _EnvType]:
        """Unit method to create new containers from failed ``Reader``."""


class CallableReaderResultN(
    ReaderResultLikeN[_FirstType, _SecondType, _ThirdType],
    reader.CanBeCalled[_ValueType, _EnvType],
):
    ...


class ReaderResultBasedN(
    CallableReaderResultN[
        _FirstType,
        _SecondType,
        _ThirdType,
        # Calls:
        'Result[_FirstType, _SecondType]',
        _ThirdType
    ]
):
    ...
