from typing import Callable, TypeVar, overload

from typing_extensions import Protocol

from returns.context import (
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import FutureResult
from returns.io import IOResult
from returns.result import Result

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType', contravariant=True)
_NewErrorType = TypeVar('_NewErrorType', covariant=True)
_EnvType = TypeVar('_EnvType', contravariant=True)


class _Altable(Protocol[_ErrorType, _NewErrorType]):
    """
    Represents type overloads for ``ret_type`` based on an error type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: RequiresContextResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextResult[_EnvType, _ValueType, _NewErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextIOResult[_EnvType, _ValueType, _NewErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> RequiresContextFutureResult[_EnvType, _ValueType, _NewErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: Result[_ValueType, _ErrorType],
    ) -> Result[_ValueType, _NewErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: IOResult[_ValueType, _ErrorType],
    ) -> IOResult[_ValueType, _NewErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_ValueType, _NewErrorType]:
        ...


def _alt(
    function: Callable[[_ErrorType], _NewErrorType],
) -> _Altable[_ErrorType, _NewErrorType]:
    ...
