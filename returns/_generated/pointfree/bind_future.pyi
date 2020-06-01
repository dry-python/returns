from typing import Callable, TypeVar

from typing_extensions import Protocol

from returns.future import Future, FutureResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)


class _BindFuture(Protocol[_ValueType, _NewValueType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...


def _bind_future(
    function: Callable[[_ValueType], Future[_NewValueType]],
) -> _BindFuture[_ValueType, _NewValueType]:
    ...
