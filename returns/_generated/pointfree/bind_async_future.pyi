from typing import Awaitable, Callable, TypeVar, overload

from typing_extensions import Protocol

from returns.context import RequiresContextFutureResult
from returns.future import Future, FutureResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType')


class _BindAsyncFuture(Protocol[_ValueType, _NewValueType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]:
        ...


def _bind_async_future(
    function: Callable[[_ValueType], Awaitable[Future[_NewValueType]]],
) -> _BindAsyncFuture[_ValueType, _NewValueType]:
    ...
