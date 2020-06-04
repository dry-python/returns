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
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType', contravariant=True)


class _Fixable(Protocol[_ErrorType, _NewValueType]):
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
    ) -> RequiresContextResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: Result[_ValueType, _ErrorType],
    ) -> Result[_NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: IOResult[_ValueType, _ErrorType],
    ) -> IOResult[_NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...


def _fix(
    function: Callable[[_ErrorType], _NewValueType],
) -> _Fixable[_ErrorType, _NewValueType]:
    ...
