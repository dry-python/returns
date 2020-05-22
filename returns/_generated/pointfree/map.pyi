from typing import Callable, TypeVar, overload

from typing_extensions import Protocol

from returns.context import (
    RequiresContext,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import Future, FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType', contravariant=True)


class _Mappable(Protocol[_ValueType, _NewValueType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: Maybe[_ValueType],
    ) -> Maybe[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        container: IO[_ValueType],
    ) -> IO[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContext[_EnvType, _ValueType],
    ) -> RequiresContext[_EnvType, _NewValueType]:
        ...

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
        container: Future[_ValueType],
    ) -> Future[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...


def _map(
    function: Callable[[_ValueType], _NewValueType],
) -> _Mappable[_ValueType, _NewValueType]:
    ...
