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


# map method:

class _Mappable(Protocol[_ValueType, _NewValueType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.
    It does not exist in runtime.

    TODO: possibly we can remove it in mypy plugin and replace it
    with a pure callable with overloads.
    """

    @overload
    def __call__(
        self,
        function: Maybe[_ValueType],
    ) -> Maybe[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        function: IO[_ValueType],
    ) -> IO[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        function: RequiresContext[_EnvType, _ValueType],
    ) -> RequiresContext[_EnvType, _NewValueType]:
        ...

    @overload
    def __call__(
        self,
        function: RequiresContextResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        function: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        function: Result[_ValueType, _ErrorType],
    ) -> Result[_NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        function: IOResult[_ValueType, _ErrorType],
    ) -> IOResult[_NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        function: Future[_ValueType],
    ) -> Future[_NewValueType]:
        ...

    @overload
    def __call__(
        self,
        function: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...


def _map(
    function: Callable[[_ValueType], _NewValueType],
) -> _Mappable[_ValueType, _NewValueType]:
    ...
